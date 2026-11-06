import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.files.FileHandle;
import com.badlogic.gdx.graphics.Pixmap;
import com.badlogic.gdx.graphics.PixmapIO;
import com.badlogic.gdx.utils.ScreenUtils;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.megacrit.cardcrawl.actions.GameActionManager;
import com.megacrit.cardcrawl.cards.AbstractCard;
import com.megacrit.cardcrawl.cards.CardGroup;
import com.megacrit.cardcrawl.cards.CardQueueItem;
import com.megacrit.cardcrawl.characters.AbstractPlayer;
import com.megacrit.cardcrawl.core.CardCrawlGame;
import com.megacrit.cardcrawl.core.OverlayMenu;
import com.megacrit.cardcrawl.core.Settings;
import com.megacrit.cardcrawl.dungeons.AbstractDungeon;
import com.megacrit.cardcrawl.events.RoomEventDialog;
import com.megacrit.cardcrawl.helpers.Hitbox;
import com.megacrit.cardcrawl.helpers.input.InputHelper;
import com.megacrit.cardcrawl.map.DungeonMap;
import com.megacrit.cardcrawl.map.MapEdge;
import com.megacrit.cardcrawl.map.MapRoomNode;
import com.megacrit.cardcrawl.monsters.AbstractMonster;
import com.megacrit.cardcrawl.potions.AbstractPotion;
import com.megacrit.cardcrawl.potions.PotionSlot;
import com.megacrit.cardcrawl.powers.AbstractPower;
import com.megacrit.cardcrawl.relics.AbstractRelic;
import com.megacrit.cardcrawl.rewards.RewardItem;
import com.megacrit.cardcrawl.rewards.chests.AbstractChest;
import com.megacrit.cardcrawl.rooms.AbstractRoom;
import com.megacrit.cardcrawl.rooms.CampfireUI;
import com.megacrit.cardcrawl.rooms.RestRoom;
import com.megacrit.cardcrawl.rooms.ShopRoom;
import com.megacrit.cardcrawl.rooms.TreasureRoom;
import com.megacrit.cardcrawl.rooms.TreasureRoomBoss;
import com.megacrit.cardcrawl.screens.CardRewardScreen;
import com.megacrit.cardcrawl.screens.CombatRewardScreen;
import com.megacrit.cardcrawl.screens.DungeonMapScreen;
import com.megacrit.cardcrawl.screens.GameOverScreen;
import com.megacrit.cardcrawl.screens.charSelect.CharacterOption;
import com.megacrit.cardcrawl.screens.charSelect.CharacterSelectScreen;
import com.megacrit.cardcrawl.screens.mainMenu.MainMenuPanelButton;
import com.megacrit.cardcrawl.screens.mainMenu.MainMenuScreen;
import com.megacrit.cardcrawl.screens.mainMenu.MenuButton;
import com.megacrit.cardcrawl.screens.select.BossRelicSelectScreen;
import com.megacrit.cardcrawl.screens.select.GridCardSelectScreen;
import com.megacrit.cardcrawl.screens.select.HandCardSelectScreen;
import com.megacrit.cardcrawl.shop.Merchant;
import com.megacrit.cardcrawl.shop.ShopScreen;
import com.megacrit.cardcrawl.shop.StorePotion;
import com.megacrit.cardcrawl.shop.StoreRelic;
import com.megacrit.cardcrawl.ui.buttons.CardSelectConfirmButton;
import com.megacrit.cardcrawl.ui.buttons.ConfirmButton;
import com.megacrit.cardcrawl.ui.buttons.EndTurnButton;
import com.megacrit.cardcrawl.ui.buttons.GridSelectConfirmButton;
import com.megacrit.cardcrawl.ui.buttons.LargeDialogOptionButton;
import com.megacrit.cardcrawl.ui.buttons.ProceedButton;
import com.megacrit.cardcrawl.ui.buttons.ReturnToMenuButton;
import com.megacrit.cardcrawl.ui.buttons.SingingBowlButton;
import com.megacrit.cardcrawl.ui.buttons.SkipCardButton;
import com.megacrit.cardcrawl.ui.campfire.AbstractCampfireOption;
import com.megacrit.cardcrawl.ui.panels.EnergyPanel;
import com.megacrit.cardcrawl.ui.panels.PotionPopUp;
import com.megacrit.cardcrawl.ui.panels.TopPanel;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.lang.instrument.Instrumentation;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

public class StsObserverAgent {
    private static final Gson GSON = new GsonBuilder().serializeNulls().create();

    public static void premain(String agentArgs, Instrumentation inst) {
        try {
            int port = 17575;
            if (agentArgs != null && !agentArgs.trim().isEmpty()) {
                port = Integer.parseInt(agentArgs.trim());
            }
            HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", port), 0);
            server.createContext("/state", new StateHandler());
            server.createContext("/action", new ActionHandler());
            server.createContext("/screenshot", new ScreenshotHandler());
            server.setExecutor(null);
            Thread t = new Thread(new Runnable() {
                @Override
                public void run() {
                    server.start();
                }
            }, "StsObserverHttpThread");
            t.setDaemon(true);
            t.start();
            System.out.println("[StsObserverAgent] Listening on http://127.0.0.1:" + port);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static Map<String, String> parseQuery(String query) {
        Map<String, String> map = new HashMap<String, String>();
        if (query == null || query.isEmpty()) return map;
        for (String pair : query.split("&")) {
            int idx = pair.indexOf('=');
            try {
                if (idx > 0) {
                    map.put(URLDecoder.decode(pair.substring(0, idx), "UTF-8"),
                            URLDecoder.decode(pair.substring(idx + 1), "UTF-8"));
                } else {
                    map.put(URLDecoder.decode(pair, "UTF-8"), "");
                }
            } catch (Exception ignored) {
            }
        }
        return map;
    }

    private static void sendJson(HttpExchange exchange, Map<String, Object> data) throws IOException {
        String json = GSON.toJson(data);
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json; charset=utf-8");
        exchange.sendResponseHeaders(200, bytes.length);
        OutputStream os = exchange.getResponseBody();
        os.write(bytes);
        os.close();
    }

    static class ActionHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            Map<String, String> q = parseQuery(exchange.getRequestURI().getRawQuery());
            String cmd = q.get("cmd");
            Map<String, Object> res = new LinkedHashMap<String, Object>();
            try {
                if ("click".equals(cmd)) {
                    final float cx = Float.parseFloat(q.get("x"));
                    final float cy = Float.parseFloat(q.get("y"));
                    final int screenX = Math.round(cx);
                    final int screenY = Settings.HEIGHT - Math.round(cy);
                    Gdx.app.postRunnable(new Runnable() {
                        @Override
                        public void run() {
                            Gdx.input.setCursorPosition(screenX, screenY);
                            InputHelper.mX = Math.round(cx);
                            InputHelper.mY = Math.round(cy);
                        }
                    });
                    Thread.sleep(50);
                    Gdx.app.postRunnable(new Runnable() {
                        @Override
                        public void run() {
                            Gdx.input.setCursorPosition(screenX, screenY);
                            InputHelper.mX = Math.round(cx);
                            InputHelper.mY = Math.round(cy);
                            InputHelper.touchDown = true;
                        }
                    });
                    Thread.sleep(50);
                    Gdx.app.postRunnable(new Runnable() {
                        @Override
                        public void run() {
                            Gdx.input.setCursorPosition(screenX, screenY);
                            InputHelper.mX = Math.round(cx);
                            InputHelper.mY = Math.round(cy);
                            InputHelper.touchUp = true;
                        }
                    });
                    Thread.sleep(60);
                    res.put("ok", true);
                    res.put("cmd", "click");
                } else if ("play_card".equals(cmd)) {
                    final int cardIndex = Integer.parseInt(q.get("cardIndex"));
                    final int targetIndex = q.containsKey("targetIndex") ? Integer.parseInt(q.get("targetIndex")) : -1;
                    final CountDownLatch latch = new CountDownLatch(1);
                    final String[] status = new String[]{"ok"};
                    Gdx.app.postRunnable(new Runnable() {
                        @Override
                        public void run() {
                            try {
                                AbstractPlayer p = AbstractDungeon.player;
                                if (p == null || p.hand == null || cardIndex < 0 || cardIndex >= p.hand.group.size()) {
                                    status[0] = "invalid_card_index";
                                    return;
                                }
                                AbstractCard card = p.hand.group.get(cardIndex);
                                AbstractMonster target = null;
                                if (targetIndex >= 0) {
                                    AbstractRoom r = AbstractDungeon.getCurrRoom();
                                    if (r != null && r.monsters != null && targetIndex < r.monsters.monsters.size()) {
                                        target = r.monsters.monsters.get(targetIndex);
                                    }
                                }
                                if (!card.canUse(p, target)) {
                                    status[0] = "cannot_use:" + card.cantUseMessage;
                                    return;
                                }
                                if (target != null && target.hb != null) {
                                    Gdx.input.setCursorPosition(Math.round(target.hb.cX), Settings.HEIGHT - Math.round(target.hb.cY));
                                } else if (card.hb != null) {
                                    Gdx.input.setCursorPosition(Math.round(card.hb.cX), Settings.HEIGHT - Math.round(card.hb.cY));
                                }
                                AbstractDungeon.actionManager.cardQueue.add(new CardQueueItem(card, target));
                            } catch (Throwable t) {
                                status[0] = "err:" + t.toString();
                            } finally {
                                latch.countDown();
                            }
                        }
                    });
                    latch.await(2, TimeUnit.SECONDS);
                    res.put("ok", "ok".equals(status[0]));
                    res.put("status", status[0]);
                } else if ("end_turn".equals(cmd)) {
                    Gdx.app.postRunnable(new Runnable() {
                        @Override
                        public void run() {
                            if (AbstractDungeon.overlayMenu != null && AbstractDungeon.overlayMenu.endTurnButton != null) {
                                Hitbox hb = (Hitbox) getField(AbstractDungeon.overlayMenu.endTurnButton, EndTurnButton.class, "hb");
                                if (hb != null) {
                                    Gdx.input.setCursorPosition(Math.round(hb.cX), Settings.HEIGHT - Math.round(hb.cY));
                                    hb.clicked = true;
                                }
                            }
                        }
                    });
                    Thread.sleep(60);
                    res.put("ok", true);
                } else if ("hand_select".equals(cmd)) {
                    final int cardIndex = Integer.parseInt(q.get("cardIndex"));
                    final CountDownLatch latch = new CountDownLatch(1);
                    Gdx.app.postRunnable(new Runnable() {
                        @Override
                        public void run() {
                            try {
                                HandCardSelectScreen hss = AbstractDungeon.handCardSelectScreen;
                                if (hss != null) {
                                    CardGroup hg = (CardGroup) getField(hss, HandCardSelectScreen.class, "hand");
                                    if (hg != null && cardIndex >= 0 && cardIndex < hg.group.size()) {
                                        AbstractCard c = hg.group.get(cardIndex);
                                        hss.hoveredCard = c;
                                        Method m = HandCardSelectScreen.class.getDeclaredMethod("selectHoveredCard");
                                        m.setAccessible(true);
                                        m.invoke(hss);
                                    }
                                }
                            } catch (Throwable ignored) {
                            } finally {
                                latch.countDown();
                            }
                        }
                    });
                    latch.await(2, TimeUnit.SECONDS);
                    res.put("ok", true);
                } else if ("scroll".equals(cmd)) {
                    final String dir = q.get("dir");
                    final int steps = q.containsKey("steps") ? Integer.parseInt(q.get("steps")) : 5;
                    for (int i = 0; i < steps; i++) {
                        Gdx.app.postRunnable(new Runnable() {
                            @Override
                            public void run() {
                                if ("up".equalsIgnoreCase(dir)) {
                                    InputHelper.scrolledUp = true;
                                } else {
                                    InputHelper.scrolledDown = true;
                                }
                            }
                        });
                        Thread.sleep(25);
                    }
                    res.put("ok", true);
                } else {
                    res.put("ok", false);
                    res.put("error", "Unknown cmd: " + cmd);
                }
            } catch (Throwable t) {
                res.put("ok", false);
                res.put("error", t.toString());
            }
            sendJson(exchange, res);
        }
    }

    static class ScreenshotHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            Map<String, String> q = parseQuery(exchange.getRequestURI().getRawQuery());
            final String path = q.get("path");
            final Map<String, Object> res = new LinkedHashMap<String, Object>();
            if (path == null || path.isEmpty()) {
                res.put("ok", false);
                res.put("error", "Missing path parameter");
                sendJson(exchange, res);
                return;
            }
            final CountDownLatch latch = new CountDownLatch(1);
            Gdx.app.postRunnable(new Runnable() {
                @Override
                public void run() {
                    Pixmap p = null;
                    Pixmap flipped = null;
                    try {
                        int w = Gdx.graphics.getWidth();
                        int h = Gdx.graphics.getHeight();
                        p = ScreenUtils.getFrameBufferPixmap(0, 0, w, h);
                        flipped = new Pixmap(w, h, p.getFormat());
                        ByteBuffer src = p.getPixels();
                        ByteBuffer dst = flipped.getPixels();
                        int rowBytes = w * 4;
                        byte[] row = new byte[rowBytes];
                        for (int y = 0; y < h; y++) {
                            src.position((h - 1 - y) * rowBytes);
                            src.get(row);
                            dst.position(y * rowBytes);
                            dst.put(row);
                        }
                        src.rewind();
                        dst.rewind();
                        File outFile = new File(path);
                        if (outFile.getParentFile() != null) {
                            outFile.getParentFile().mkdirs();
                        }
                        PixmapIO.writePNG(new FileHandle(outFile), flipped);
                        res.put("ok", true);
                        res.put("path", outFile.getAbsolutePath());
                    } catch (Throwable t) {
                        res.put("ok", false);
                        res.put("error", t.toString());
                    } finally {
                        if (p != null) p.dispose();
                        if (flipped != null) flipped.dispose();
                        latch.countDown();
                    }
                }
            });
            try {
                latch.await(5, TimeUnit.SECONDS);
            } catch (InterruptedException ignored) {
            }
            sendJson(exchange, res);
        }
    }

    private static Object getField(Object obj, Class<?> cls, String fieldName) {
        try {
            Field f = cls.getDeclaredField(fieldName);
            f.setAccessible(true);
            return f.get(obj);
        } catch (Exception e) {
            return null;
        }
    }

    private static boolean getBoolField(Object obj, Class<?> cls, String fieldName, boolean def) {
        Object val = getField(obj, cls, fieldName);
        return val instanceof Boolean ? (Boolean) val : def;
    }

    private static int getIntField(Object obj, Class<?> cls, String fieldName, int def) {
        Object val = getField(obj, cls, fieldName);
        return val instanceof Number ? ((Number) val).intValue() : def;
    }

    private static float getFloatField(Object obj, Class<?> cls, String fieldName, float def) {
        Object val = getField(obj, cls, fieldName);
        return val instanceof Number ? ((Number) val).floatValue() : def;
    }

    private static String getStrField(Object obj, Class<?> cls, String fieldName) {
        Object val = getField(obj, cls, fieldName);
        return val != null ? val.toString() : null;
    }

    private static Map<String, Object> hbMap(Hitbox hb) {
        if (hb == null) return null;
        Map<String, Object> m = new LinkedHashMap<String, Object>();
        m.put("cx", hb.cX);
        m.put("cy", hb.cY);
        m.put("w", hb.width);
        m.put("h", hb.height);
        m.put("hovered", hb.hovered);
        return m;
    }

    private static Map<String, Object> cardMap(AbstractCard c, int index, boolean checkPlayable) {
        if (c == null) return null;
        Map<String, Object> m = new LinkedHashMap<String, Object>();
        m.put("index", index);
        m.put("id", c.cardID);
        m.put("name", c.name);
        m.put("upgraded", c.upgraded);
        m.put("timesUpgraded", c.timesUpgraded);
        m.put("cost", c.cost);
        m.put("costForTurn", c.costForTurn);
        m.put("freeToPlayOnce", c.freeToPlayOnce);
        m.put("type", c.type != null ? c.type.name() : null);
        m.put("rarity", c.rarity != null ? c.rarity.name() : null);
        m.put("color", c.color != null ? c.color.name() : null);
        m.put("target", c.target != null ? c.target.name() : null);
        m.put("damage", c.damage);
        m.put("baseDamage", c.baseDamage);
        m.put("block", c.block);
        m.put("baseBlock", c.baseBlock);
        m.put("magicNumber", c.magicNumber);
        m.put("baseMagicNumber", c.baseMagicNumber);
        m.put("exhaust", c.exhaust);
        m.put("isEthereal", c.isEthereal);
        m.put("price", c.price);
        m.put("hb", hbMap(c.hb));
        if (checkPlayable && AbstractDungeon.player != null) {
            boolean canUse = false;
            try {
                if (c.target == AbstractCard.CardTarget.ENEMY || c.target == AbstractCard.CardTarget.SELF_AND_ENEMY) {
                    AbstractRoom room = AbstractDungeon.getCurrRoom();
                    if (room != null && room.monsters != null && room.monsters.monsters != null) {
                        for (AbstractMonster mon : room.monsters.monsters) {
                            if (mon != null && !mon.isDeadOrEscaped() && c.canUse(AbstractDungeon.player, mon)) {
                                canUse = true;
                                break;
                            }
                        }
                    }
                } else {
                    canUse = c.canUse(AbstractDungeon.player, null);
                }
            } catch (Exception ignored) {
            }
            m.put("canUse", canUse);
        }
        return m;
    }

    static class StateHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            Map<String, Object> root;
            try {
                root = buildState();
            } catch (Throwable t) {
                root = new LinkedHashMap<String, Object>();
                root.put("error", t.toString());
            }
            sendJson(exchange, root);
        }
    }

    private static Map<String, Object> buildState() {
        Map<String, Object> root = new LinkedHashMap<String, Object>();
        root.put("mode", CardCrawlGame.mode != null ? CardCrawlGame.mode.name() : "NULL");
        root.put("inRun", CardCrawlGame.isInARun());
        Map<String, Object> win = new LinkedHashMap<String, Object>();
        win.put("width", Settings.WIDTH);
        win.put("height", Settings.HEIGHT);
        root.put("window", win);

        MainMenuScreen mms = CardCrawlGame.mainMenuScreen;
        if (mms != null && CardCrawlGame.mode == CardCrawlGame.GameMode.CHAR_SELECT) {
            Map<String, Object> mm = new LinkedHashMap<String, Object>();
            mm.put("screen", mms.screen != null ? mms.screen.name() : null);
            List<Map<String, Object>> btns = new ArrayList<Map<String, Object>>();
            if (mms.buttons != null) {
                for (int i = 0; i < mms.buttons.size(); i++) {
                    MenuButton b = mms.buttons.get(i);
                    if (b == null) continue;
                    Map<String, Object> bm = new LinkedHashMap<String, Object>();
                    bm.put("index", i);
                    bm.put("result", b.result != null ? b.result.name() : null);
                    bm.put("label", getStrField(b, MenuButton.class, "label"));
                    bm.put("hidden", getBoolField(b, MenuButton.class, "hidden", false));
                    bm.put("hb", hbMap(b.hb));
                    btns.add(bm);
                }
            }
            mm.put("buttons", btns);

            if (mms.panelScreen != null && mms.panelScreen.panels != null) {
                List<Map<String, Object>> panels = new ArrayList<Map<String, Object>>();
                for (int i = 0; i < mms.panelScreen.panels.size(); i++) {
                    MainMenuPanelButton p = mms.panelScreen.panels.get(i);
                    if (p == null) continue;
                    Map<String, Object> pm = new LinkedHashMap<String, Object>();
                    pm.put("index", i);
                    Object res = getField(p, MainMenuPanelButton.class, "result");
                    pm.put("result", res != null ? res.toString() : null);
                    pm.put("header", getStrField(p, MainMenuPanelButton.class, "header"));
                    pm.put("hb", hbMap(p.hb));
                    panels.add(pm);
                }
                mm.put("panels", panels);
            }

            CharacterSelectScreen css = mms.charSelectScreen;
            if (css != null) {
                Map<String, Object> cs = new LinkedHashMap<String, Object>();
                cs.put("isAscensionMode", css.isAscensionMode);
                cs.put("ascensionLevel", css.ascensionLevel);
                Hitbox ascHb = (Hitbox) getField(css, CharacterSelectScreen.class, "ascensionModeHb");
                cs.put("ascensionHb", hbMap(ascHb));
                Hitbox ascLeftHb = (Hitbox) getField(css, CharacterSelectScreen.class, "ascLeftHb");
                cs.put("ascLeftHb", hbMap(ascLeftHb));
                if (css.confirmButton != null) {
                    Map<String, Object> cb = new LinkedHashMap<String, Object>();
                    cb.put("isDisabled", css.confirmButton.isDisabled);
                    cb.put("isHidden", getBoolField(css.confirmButton, ConfirmButton.class, "isHidden", true));
                    cb.put("hb", hbMap(css.confirmButton.hb));
                    cs.put("confirmButton", cb);
                }
                List<Map<String, Object>> opts = new ArrayList<Map<String, Object>>();
                if (css.options != null) {
                    for (int i = 0; i < css.options.size(); i++) {
                        CharacterOption o = css.options.get(i);
                        if (o == null) continue;
                        Map<String, Object> om = new LinkedHashMap<String, Object>();
                        om.put("index", i);
                        om.put("name", o.name);
                        om.put("chosenClass", (o.c != null && o.c.chosenClass != null) ? o.c.chosenClass.name() : null);
                        om.put("selected", o.selected);
                        om.put("locked", o.locked);
                        om.put("hb", hbMap(o.hb));
                        opts.add(om);
                    }
                }
                cs.put("options", opts);
                mm.put("charSelect", cs);
            }
            root.put("mainMenu", mm);
        }

        if (AbstractDungeon.player != null && (CardCrawlGame.mode == CardCrawlGame.GameMode.GAMEPLAY || CardCrawlGame.mode == CardCrawlGame.GameMode.DUNGEON_TRANSITION)) {
            Map<String, Object> d = new LinkedHashMap<String, Object>();
            d.put("id", AbstractDungeon.id);
            d.put("name", AbstractDungeon.name);
            d.put("actNum", AbstractDungeon.actNum);
            d.put("floorNum", AbstractDungeon.floorNum);
            d.put("bossKey", AbstractDungeon.bossKey);
            d.put("screen", AbstractDungeon.screen != null ? AbstractDungeon.screen.name() : "NULL");
            d.put("isScreenUp", AbstractDungeon.isScreenUp);
            d.put("isFadingIn", AbstractDungeon.isFadingIn);
            d.put("isFadingOut", AbstractDungeon.isFadingOut);
            d.put("waitingOnFadeOut", AbstractDungeon.waitingOnFadeOut);
            d.put("firstRoomChosen", AbstractDungeon.firstRoomChosen);
            root.put("dungeon", d);

            AbstractRoom room = null;
            try {
                room = AbstractDungeon.getCurrRoom();
            } catch (Exception ignored) {
            }
            if (room != null) {
                Map<String, Object> rm = new LinkedHashMap<String, Object>();
                rm.put("className", room.getClass().getSimpleName());
                rm.put("phase", room.phase != null ? room.phase.name() : "NULL");
                rm.put("isBattleOver", room.isBattleOver);
                rm.put("rewardTime", room.rewardTime);
                root.put("room", rm);
            }

            GameActionManager am = AbstractDungeon.actionManager;
            if (am != null) {
                Map<String, Object> amm = new LinkedHashMap<String, Object>();
                amm.put("phase", am.phase != null ? am.phase.name() : "NULL");
                amm.put("turnHasEnded", am.turnHasEnded);
                amm.put("hasControl", am.hasControl);
                amm.put("usingCard", am.usingCard);
                amm.put("actionsCount", am.actions != null ? am.actions.size() : 0);
                amm.put("cardQueueCount", am.cardQueue != null ? am.cardQueue.size() : 0);
                amm.put("turn", GameActionManager.turn);
                root.put("actionManager", amm);
            }

            AbstractPlayer p = AbstractDungeon.player;
            Map<String, Object> pm = new LinkedHashMap<String, Object>();
            pm.put("currentHealth", p.currentHealth);
            pm.put("maxHealth", p.maxHealth);
            pm.put("currentBlock", p.currentBlock);
            pm.put("gold", p.gold);
            pm.put("energy", EnergyPanel.totalCount);
            pm.put("isDraggingCard", p.isDraggingCard);
            pm.put("inSingleTargetMode", p.inSingleTargetMode);
            pm.put("isEndingTurn", p.isEndingTurn);
            pm.put("hoveredCard", p.hoveredCard != null ? p.hoveredCard.cardID : null);

            List<Map<String, Object>> powers = new ArrayList<Map<String, Object>>();
            if (p.powers != null) {
                for (AbstractPower pow : p.powers) {
                    if (pow == null) continue;
                    Map<String, Object> pwm = new LinkedHashMap<String, Object>();
                    pwm.put("id", pow.ID);
                    pwm.put("name", pow.name);
                    pwm.put("amount", pow.amount);
                    powers.add(pwm);
                }
            }
            pm.put("powers", powers);

            List<Map<String, Object>> relics = new ArrayList<Map<String, Object>>();
            if (p.relics != null) {
                for (AbstractRelic rel : p.relics) {
                    if (rel == null) continue;
                    Map<String, Object> rlm = new LinkedHashMap<String, Object>();
                    rlm.put("id", rel.relicId);
                    rlm.put("name", rel.name);
                    rlm.put("counter", rel.counter);
                    rlm.put("hb", hbMap(rel.hb));
                    relics.add(rlm);
                }
            }
            pm.put("relics", relics);

            List<Map<String, Object>> potions = new ArrayList<Map<String, Object>>();
            if (p.potions != null) {
                for (int i = 0; i < p.potions.size(); i++) {
                    AbstractPotion pot = p.potions.get(i);
                    if (pot == null) continue;
                    Map<String, Object> ptm = new LinkedHashMap<String, Object>();
                    ptm.put("slot", i);
                    ptm.put("id", pot.ID);
                    ptm.put("name", pot.name);
                    ptm.put("isEmpty", pot instanceof PotionSlot);
                    boolean canUse = false;
                    try {
                        canUse = !(pot instanceof PotionSlot) && pot.canUse();
                    } catch (Exception ignored) {
                    }
                    ptm.put("canUse", canUse);
                    ptm.put("canDiscard", !(pot instanceof PotionSlot) && pot.canDiscard());
                    ptm.put("isThrown", pot.isThrown);
                    ptm.put("targetRequired", pot.targetRequired);
                    ptm.put("hb", hbMap(pot.hb));
                    potions.add(ptm);
                }
            }
            pm.put("potions", potions);

            if (AbstractDungeon.topPanel != null && AbstractDungeon.topPanel.potionUi != null) {
                PotionPopUp pui = AbstractDungeon.topPanel.potionUi;
                Map<String, Object> puim = new LinkedHashMap<String, Object>();
                puim.put("isHidden", pui.isHidden);
                puim.put("targetMode", pui.targetMode);
                puim.put("topHb", hbMap((Hitbox) getField(pui, PotionPopUp.class, "hbTop")));
                puim.put("botHb", hbMap((Hitbox) getField(pui, PotionPopUp.class, "hbBot")));
                pm.put("potionPopUp", puim);
            }

            List<Map<String, Object>> hand = new ArrayList<Map<String, Object>>();
            if (p.hand != null && p.hand.group != null) {
                for (int i = 0; i < p.hand.group.size(); i++) {
                    hand.add(cardMap(p.hand.group.get(i), i, true));
                }
            }
            pm.put("hand", hand);
            pm.put("drawPileSize", p.drawPile != null ? p.drawPile.size() : 0);
            pm.put("discardPileSize", p.discardPile != null ? p.discardPile.size() : 0);
            pm.put("exhaustPileSize", p.exhaustPile != null ? p.exhaustPile.size() : 0);

            List<Map<String, Object>> masterDeck = new ArrayList<Map<String, Object>>();
            if (p.masterDeck != null && p.masterDeck.group != null) {
                for (int i = 0; i < p.masterDeck.group.size(); i++) {
                    AbstractCard c = p.masterDeck.group.get(i);
                    if (c == null) continue;
                    Map<String, Object> cm = new LinkedHashMap<String, Object>();
                    cm.put("index", i);
                    cm.put("id", c.cardID);
                    cm.put("name", c.name);
                    cm.put("upgraded", c.upgraded);
                    cm.put("type", c.type != null ? c.type.name() : null);
                    cm.put("cost", c.cost);
                    masterDeck.add(cm);
                }
            }
            pm.put("masterDeck", masterDeck);
            root.put("player", pm);

            // Monsters
            List<Map<String, Object>> monsters = new ArrayList<Map<String, Object>>();
            if (room != null && room.monsters != null && room.monsters.monsters != null) {
                for (int i = 0; i < room.monsters.monsters.size(); i++) {
                    AbstractMonster m = room.monsters.monsters.get(i);
                    if (m == null) continue;
                    Map<String, Object> mm = new LinkedHashMap<String, Object>();
                    mm.put("index", i);
                    mm.put("id", m.id);
                    mm.put("name", m.name);
                    mm.put("currentHealth", m.currentHealth);
                    mm.put("maxHealth", m.maxHealth);
                    mm.put("currentBlock", m.currentBlock);
                    mm.put("isDead", m.isDead);
                    mm.put("isDying", m.isDying);
                    mm.put("isEscaping", m.isEscaping);
                    mm.put("halfDead", m.halfDead);
                    mm.put("intent", m.intent != null ? m.intent.name() : "NULL");
                    mm.put("intentDmg", m.getIntentDmg());
                    mm.put("intentBaseDmg", m.getIntentBaseDmg());
                    mm.put("intentMultiAmt", getIntField(m, AbstractMonster.class, "intentMultiAmt", -1));
                    mm.put("isMultiDmg", getBoolField(m, AbstractMonster.class, "isMultiDmg", false));
                    mm.put("moveName", m.moveName);
                    mm.put("hb", hbMap(m.hb));
                    List<Map<String, Object>> mpowers = new ArrayList<Map<String, Object>>();
                    if (m.powers != null) {
                        for (AbstractPower pow : m.powers) {
                            if (pow == null) continue;
                            Map<String, Object> pwm = new LinkedHashMap<String, Object>();
                            pwm.put("id", pow.ID);
                            pwm.put("name", pow.name);
                            pwm.put("amount", pow.amount);
                            mpowers.add(pwm);
                        }
                    }
                    mm.put("powers", mpowers);
                    monsters.add(mm);
                }
            }
            root.put("monsters", monsters);

            // Overlay buttons
            OverlayMenu om = AbstractDungeon.overlayMenu;
            if (om != null) {
                Map<String, Object> ob = new LinkedHashMap<String, Object>();
                if (om.endTurnButton != null) {
                    Map<String, Object> et = new LinkedHashMap<String, Object>();
                    et.put("enabled", om.endTurnButton.enabled);
                    et.put("isHidden", getBoolField(om.endTurnButton, EndTurnButton.class, "isHidden", true));
                    et.put("hb", hbMap((Hitbox) getField(om.endTurnButton, EndTurnButton.class, "hb")));
                    ob.put("endTurn", et);
                }
                if (om.proceedButton != null) {
                    Map<String, Object> pr = new LinkedHashMap<String, Object>();
                    pr.put("isHidden", getBoolField(om.proceedButton, ProceedButton.class, "isHidden", true));
                    pr.put("label", getStrField(om.proceedButton, ProceedButton.class, "label"));
                    pr.put("hb", hbMap((Hitbox) getField(om.proceedButton, ProceedButton.class, "hb")));
                    ob.put("proceed", pr);
                }
                if (om.cancelButton != null) {
                    Map<String, Object> ca = new LinkedHashMap<String, Object>();
                    ca.put("isHidden", om.cancelButton.isHidden);
                    ca.put("buttonText", om.cancelButton.buttonText);
                    ca.put("hb", hbMap(om.cancelButton.hb));
                    ob.put("cancel", ca);
                }
                if (AbstractDungeon.topPanel != null) {
                    Map<String, Object> tp = new LinkedHashMap<String, Object>();
                    tp.put("mapDisabled", getBoolField(AbstractDungeon.topPanel, TopPanel.class, "mapButtonDisabled", false));
                    tp.put("mapHb", hbMap(AbstractDungeon.topPanel.mapHb));
                    ob.put("topPanel", tp);
                }
                root.put("overlay", ob);
            }

            // Event options
            Map<String, Object> ev = new LinkedHashMap<String, Object>();
            if (room != null && room.event != null) {
                ev.put("eventName", room.event.getClass().getSimpleName());
            }
            List<Map<String, Object>> roomOpts = new ArrayList<Map<String, Object>>();
            if (RoomEventDialog.optionList != null) {
                for (int i = 0; i < RoomEventDialog.optionList.size(); i++) {
                    LargeDialogOptionButton btn = RoomEventDialog.optionList.get(i);
                    if (btn == null) continue;
                    Map<String, Object> bm = new LinkedHashMap<String, Object>();
                    bm.put("index", i);
                    bm.put("slot", btn.slot);
                    bm.put("msg", btn.msg);
                    bm.put("isDisabled", btn.isDisabled);
                    bm.put("pressed", btn.pressed);
                    bm.put("hb", hbMap(btn.hb));
                    roomOpts.add(bm);
                }
            }
            ev.put("roomEventOptions", roomOpts);

            List<Map<String, Object>> imgOpts = new ArrayList<Map<String, Object>>();
            if (room != null && room.event != null && room.event.imageEventText != null && room.event.imageEventText.optionList != null) {
                for (int i = 0; i < room.event.imageEventText.optionList.size(); i++) {
                    LargeDialogOptionButton btn = room.event.imageEventText.optionList.get(i);
                    if (btn == null) continue;
                    Map<String, Object> bm = new LinkedHashMap<String, Object>();
                    bm.put("index", i);
                    bm.put("slot", btn.slot);
                    bm.put("msg", btn.msg);
                    bm.put("isDisabled", btn.isDisabled);
                    bm.put("pressed", btn.pressed);
                    bm.put("hb", hbMap(btn.hb));
                    imgOpts.add(bm);
                }
            }
            ev.put("imageEventOptions", imgOpts);
            root.put("event", ev);

            // CombatRewardScreen
            CombatRewardScreen crs = AbstractDungeon.combatRewardScreen;
            if (crs != null && crs.rewards != null) {
                List<Map<String, Object>> rews = new ArrayList<Map<String, Object>>();
                for (int i = 0; i < crs.rewards.size(); i++) {
                    RewardItem r = crs.rewards.get(i);
                    if (r == null) continue;
                    Map<String, Object> rwm = new LinkedHashMap<String, Object>();
                    rwm.put("index", i);
                    rwm.put("type", r.type != null ? r.type.name() : null);
                    rwm.put("text", r.text);
                    rwm.put("goldAmt", r.goldAmt);
                    rwm.put("relicId", r.relic != null ? r.relic.relicId : null);
                    rwm.put("potionId", r.potion != null ? r.potion.ID : null);
                    rwm.put("isDone", r.isDone);
                    rwm.put("ignoreReward", r.ignoreReward);
                    rwm.put("hb", hbMap(r.hb));
                    rews.add(rwm);
                }
                root.put("combatRewards", rews);
            }

            // CardRewardScreen
            CardRewardScreen cardRs = AbstractDungeon.cardRewardScreen;
            if (cardRs != null) {
                Map<String, Object> crm = new LinkedHashMap<String, Object>();
                List<Map<String, Object>> rcards = new ArrayList<Map<String, Object>>();
                if (cardRs.rewardGroup != null) {
                    for (int i = 0; i < cardRs.rewardGroup.size(); i++) {
                        rcards.add(cardMap(cardRs.rewardGroup.get(i), i, false));
                    }
                }
                crm.put("cards", rcards);
                SkipCardButton sk = (SkipCardButton) getField(cardRs, CardRewardScreen.class, "skipButton");
                if (sk != null) {
                    Map<String, Object> skm = new LinkedHashMap<String, Object>();
                    skm.put("isHidden", getBoolField(sk, SkipCardButton.class, "isHidden", true));
                    skm.put("hb", hbMap(sk.hb));
                    crm.put("skipButton", skm);
                }
                SingingBowlButton bw = (SingingBowlButton) getField(cardRs, CardRewardScreen.class, "bowlButton");
                if (bw != null) {
                    Map<String, Object> bwm = new LinkedHashMap<String, Object>();
                    bwm.put("isHidden", bw.isHidden());
                    bwm.put("hb", hbMap(bw.hb));
                    crm.put("bowlButton", bwm);
                }
                root.put("cardReward", crm);
            }

            // BossRelicSelectScreen
            BossRelicSelectScreen brs = AbstractDungeon.bossRelicScreen;
            if (brs != null && brs.relics != null) {
                List<Map<String, Object>> brelics = new ArrayList<Map<String, Object>>();
                for (int i = 0; i < brs.relics.size(); i++) {
                    AbstractRelic r = brs.relics.get(i);
                    if (r == null) continue;
                    Map<String, Object> brm = new LinkedHashMap<String, Object>();
                    brm.put("index", i);
                    brm.put("id", r.relicId);
                    brm.put("name", r.name);
                    brm.put("hb", hbMap(r.hb));
                    brelics.add(brm);
                }
                root.put("bossRelics", brelics);
            }

            // Campfire (RestRoom)
            if (room instanceof RestRoom) {
                CampfireUI cui = ((RestRoom) room).campfireUI;
                if (cui != null) {
                    Map<String, Object> cm = new LinkedHashMap<String, Object>();
                    cm.put("somethingSelected", cui.somethingSelected);
                    cm.put("hidden", CampfireUI.hidden);
                    @SuppressWarnings("unchecked")
                    ArrayList<AbstractCampfireOption> btns = (ArrayList<AbstractCampfireOption>) getField(cui, CampfireUI.class, "buttons");
                    List<Map<String, Object>> cbtns = new ArrayList<Map<String, Object>>();
                    if (btns != null) {
                        for (int i = 0; i < btns.size(); i++) {
                            AbstractCampfireOption o = btns.get(i);
                            if (o == null) continue;
                            Map<String, Object> om2 = new LinkedHashMap<String, Object>();
                            om2.put("index", i);
                            om2.put("type", o.getClass().getSimpleName());
                            om2.put("label", getStrField(o, AbstractCampfireOption.class, "label"));
                            om2.put("usable", o.usable);
                            om2.put("hb", hbMap(o.hb));
                            cbtns.add(om2);
                        }
                    }
                    cm.put("options", cbtns);
                    root.put("campfire", cm);
                }
            }

            // TreasureRoom / TreasureRoomBoss
            if (room instanceof TreasureRoom) {
                AbstractChest ch = ((TreasureRoom) room).chest;
                if (ch != null) {
                    Map<String, Object> chm = new LinkedHashMap<String, Object>();
                    chm.put("isOpen", ch.isOpen);
                    chm.put("hb", hbMap((Hitbox) getField(ch, AbstractChest.class, "hb")));
                    root.put("treasure", chm);
                }
            } else if (room instanceof TreasureRoomBoss) {
                AbstractChest ch = ((TreasureRoomBoss) room).chest;
                if (ch != null) {
                    Map<String, Object> chm = new LinkedHashMap<String, Object>();
                    chm.put("isOpen", ch.isOpen);
                    chm.put("choseRelic", ((TreasureRoomBoss) room).choseRelic);
                    chm.put("hb", hbMap((Hitbox) getField(ch, AbstractChest.class, "hb")));
                    root.put("treasure", chm);
                }
            }

            // Shop
            Map<String, Object> sh = new LinkedHashMap<String, Object>();
            if (room instanceof ShopRoom) {
                Merchant merch = ((ShopRoom) room).merchant;
                if (merch != null) {
                    sh.put("merchantHb", hbMap(merch.hb));
                }
            }
            ShopScreen ss = AbstractDungeon.shopScreen;
            if (ss != null) {
                List<Map<String, Object>> colCards = new ArrayList<Map<String, Object>>();
                if (ss.coloredCards != null) {
                    for (int i = 0; i < ss.coloredCards.size(); i++) {
                        colCards.add(cardMap(ss.coloredCards.get(i), i, false));
                    }
                }
                sh.put("coloredCards", colCards);

                List<Map<String, Object>> clessCards = new ArrayList<Map<String, Object>>();
                if (ss.colorlessCards != null) {
                    for (int i = 0; i < ss.colorlessCards.size(); i++) {
                        clessCards.add(cardMap(ss.colorlessCards.get(i), i, false));
                    }
                }
                sh.put("colorlessCards", clessCards);

                @SuppressWarnings("unchecked")
                ArrayList<StoreRelic> sRelics = (ArrayList<StoreRelic>) getField(ss, ShopScreen.class, "relics");
                List<Map<String, Object>> sRelicList = new ArrayList<Map<String, Object>>();
                if (sRelics != null) {
                    for (int i = 0; i < sRelics.size(); i++) {
                        StoreRelic sr = sRelics.get(i);
                        if (sr == null || sr.relic == null) continue;
                        Map<String, Object> srm = new LinkedHashMap<String, Object>();
                        srm.put("index", i);
                        srm.put("id", sr.relic.relicId);
                        srm.put("name", sr.relic.name);
                        srm.put("price", sr.price);
                        srm.put("isPurchased", sr.isPurchased);
                        srm.put("hb", hbMap(sr.relic.hb));
                        sRelicList.add(srm);
                    }
                }
                sh.put("relics", sRelicList);

                @SuppressWarnings("unchecked")
                ArrayList<StorePotion> sPots = (ArrayList<StorePotion>) getField(ss, ShopScreen.class, "potions");
                List<Map<String, Object>> sPotList = new ArrayList<Map<String, Object>>();
                if (sPots != null) {
                    for (int i = 0; i < sPots.size(); i++) {
                        StorePotion sp = sPots.get(i);
                        if (sp == null || sp.potion == null) continue;
                        Map<String, Object> spm = new LinkedHashMap<String, Object>();
                        spm.put("index", i);
                        spm.put("id", sp.potion.ID);
                        spm.put("name", sp.potion.name);
                        spm.put("price", sp.price);
                        spm.put("isPurchased", sp.isPurchased);
                        spm.put("hb", hbMap(sp.potion.hb));
                        sPotList.add(spm);
                    }
                }
                sh.put("potions", sPotList);
                sh.put("purgeAvailable", ss.purgeAvailable);
                sh.put("purgeCost", ShopScreen.actualPurgeCost);
                sh.put("purgeX", getFloatField(ss, ShopScreen.class, "purgeCardX", 0f));
                sh.put("purgeY", getFloatField(ss, ShopScreen.class, "purgeCardY", 0f));
            }
            root.put("shop", sh);

            // GridCardSelectScreen
            GridCardSelectScreen gss = AbstractDungeon.gridSelectScreen;
            if (gss != null) {
                Map<String, Object> gm = new LinkedHashMap<String, Object>();
                gm.put("forUpgrade", gss.forUpgrade);
                gm.put("forPurge", gss.forPurge);
                gm.put("forTransform", gss.forTransform);
                gm.put("confirmScreenUp", gss.confirmScreenUp);
                gm.put("isJustForConfirming", gss.isJustForConfirming);
                gm.put("anyNumber", gss.anyNumber);
                gm.put("numCards", getIntField(gss, GridCardSelectScreen.class, "numCards", 0));
                gm.put("selectedCount", gss.selectedCards != null ? gss.selectedCards.size() : 0);
                if (gss.confirmButton != null) {
                    Map<String, Object> cb = new LinkedHashMap<String, Object>();
                    cb.put("isDisabled", gss.confirmButton.isDisabled);
                    cb.put("isHidden", getBoolField(gss.confirmButton, GridSelectConfirmButton.class, "isHidden", true));
                    cb.put("hb", hbMap(gss.confirmButton.hb));
                    gm.put("confirmButton", cb);
                }
                List<Map<String, Object>> gcards = new ArrayList<Map<String, Object>>();
                if (gss.targetGroup != null && gss.targetGroup.group != null) {
                    for (int i = 0; i < gss.targetGroup.group.size(); i++) {
                        gcards.add(cardMap(gss.targetGroup.group.get(i), i, false));
                    }
                }
                gm.put("cards", gcards);
                root.put("gridSelect", gm);
            }

            // HandCardSelectScreen
            HandCardSelectScreen hss = AbstractDungeon.handCardSelectScreen;
            if (hss != null) {
                Map<String, Object> hm = new LinkedHashMap<String, Object>();
                hm.put("numCardsToSelect", hss.numCardsToSelect);
                hm.put("numSelected", hss.numSelected);
                hm.put("canPickZero", hss.canPickZero);
                hm.put("upTo", hss.upTo);
                hm.put("anyNumber", getBoolField(hss, HandCardSelectScreen.class, "anyNumber", false));
                hm.put("forUpgrade", getBoolField(hss, HandCardSelectScreen.class, "forUpgrade", false));
                hm.put("forTransform", getBoolField(hss, HandCardSelectScreen.class, "forTransform", false));
                hm.put("selectionReason", hss.selectionReason);
                if (hss.button != null) {
                    Map<String, Object> cb = new LinkedHashMap<String, Object>();
                    cb.put("isDisabled", hss.button.isDisabled);
                    cb.put("isHidden", getBoolField(hss.button, CardSelectConfirmButton.class, "isHidden", true));
                    cb.put("hb", hbMap(hss.button.hb));
                    hm.put("confirmButton", cb);
                }
                CardGroup hGroup = (CardGroup) getField(hss, HandCardSelectScreen.class, "hand");
                List<Map<String, Object>> hcards = new ArrayList<Map<String, Object>>();
                if (hGroup != null && hGroup.group != null) {
                    for (int i = 0; i < hGroup.group.size(); i++) {
                        hcards.add(cardMap(hGroup.group.get(i), i, false));
                    }
                }
                hm.put("handCards", hcards);
                List<Map<String, Object>> scards = new ArrayList<Map<String, Object>>();
                if (hss.selectedCards != null && hss.selectedCards.group != null) {
                    for (int i = 0; i < hss.selectedCards.group.size(); i++) {
                        scards.add(cardMap(hss.selectedCards.group.get(i), i, false));
                    }
                }
                hm.put("selectedCards", scards);
                root.put("handSelect", hm);
            }

            // Map
            if (AbstractDungeon.map != null) {
                Map<String, Object> mp = new LinkedHashMap<String, Object>();
                MapRoomNode curr = AbstractDungeon.currMapNode;
                mp.put("currX", curr != null ? curr.x : -1);
                mp.put("currY", curr != null ? curr.y : -1);
                mp.put("offsetY", DungeonMapScreen.offsetY);
                if (AbstractDungeon.dungeonMapScreen != null && AbstractDungeon.dungeonMapScreen.map != null) {
                    DungeonMap dm = AbstractDungeon.dungeonMapScreen.map;
                    mp.put("atBoss", dm.atBoss);
                    mp.put("bossHb", hbMap(dm.bossHb));
                }
                List<Map<String, Object>> nodes = new ArrayList<Map<String, Object>>();
                for (int y = 0; y < AbstractDungeon.map.size(); y++) {
                    ArrayList<MapRoomNode> row = AbstractDungeon.map.get(y);
                    if (row == null) continue;
                    for (int x = 0; x < row.size(); x++) {
                        MapRoomNode n = row.get(x);
                        if (n == null || !n.hasEdges()) continue;
                        Map<String, Object> nm = new LinkedHashMap<String, Object>();
                        nm.put("x", n.x);
                        nm.put("y", n.y);
                        nm.put("symbol", n.getRoomSymbol(true));
                        nm.put("hasEmeraldKey", n.hasEmeraldKey);
                        nm.put("taken", n.taken);
                        nm.put("hb", hbMap(n.hb));
                        boolean playable = false;
                        if (!AbstractDungeon.firstRoomChosen) {
                            playable = (n.y == 0);
                        } else if (curr != null) {
                            try {
                                playable = curr.isConnectedTo(n) || curr.wingedIsConnectedTo(n);
                            } catch (Exception ignored) {
                            }
                        }
                        nm.put("playable", playable);
                        List<Map<String, Integer>> edges = new ArrayList<Map<String, Integer>>();
                        if (n.getEdges() != null) {
                            for (MapEdge e : n.getEdges()) {
                                if (e == null) continue;
                                Map<String, Integer> em = new LinkedHashMap<String, Integer>();
                                em.put("dstX", e.dstX);
                                em.put("dstY", e.dstY);
                                edges.add(em);
                            }
                        }
                        nm.put("edges", edges);
                        nodes.add(nm);
                    }
                }
                mp.put("nodes", nodes);
                root.put("map", mp);
            }

            // Game Over (Victory / Death)
            Map<String, Object> go = new LinkedHashMap<String, Object>();
            go.put("isVictory", GameOverScreen.isVictory);
            if (AbstractDungeon.deathScreen != null) {
                ReturnToMenuButton rtb = (ReturnToMenuButton) getField(AbstractDungeon.deathScreen, GameOverScreen.class, "returnButton");
                if (rtb != null) {
                    Map<String, Object> rtbm = new LinkedHashMap<String, Object>();
                    rtbm.put("show", rtb.show);
                    rtbm.put("hb", hbMap(rtb.hb));
                    go.put("deathReturnButton", rtbm);
                }
            }
            if (AbstractDungeon.victoryScreen != null) {
                ReturnToMenuButton rtb = (ReturnToMenuButton) getField(AbstractDungeon.victoryScreen, GameOverScreen.class, "returnButton");
                if (rtb != null) {
                    Map<String, Object> rtbm = new LinkedHashMap<String, Object>();
                    rtbm.put("show", rtb.show);
                    rtbm.put("hb", hbMap(rtb.hb));
                    go.put("victoryReturnButton", rtbm);
                }
            }
            root.put("gameOver", go);
        }

        return root;
    }
}
