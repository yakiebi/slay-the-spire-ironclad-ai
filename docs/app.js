(function () {
  const DATA = window.EXPERIMENT_DATA;
  if (!DATA) return;

  Chart.defaults.color = '#9c96a8';
  Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.07)';
  Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";

  // 1. Floor Reached & Playtime Chart
  const runsCtx = document.getElementById('runsProgressionChart').getContext('2d');
  const runLabels = DATA.runs.map(r => `Run #${r.Run_Number} (${r.Iteration})`);
  const floorData = DATA.runs.map(r => r.Floor_Reached);
  const timeData = DATA.runs.map(r => r.Playtime_Sec);
  const barColors = DATA.runs.map(r => {
    if (r.Outcome === 'VICTORY') return '#51cf66';
    if (r.Floor_Reached >= 50) return '#ffd43b';
    if (r.Floor_Reached >= 35) return '#f59f00';
    if (r.Floor_Reached >= 18) return '#e03131';
    return '#862e9c';
  });

  new Chart(runsCtx, {
    type: 'bar',
    data: {
      labels: runLabels,
      datasets: [
        {
          label: 'Floor Reached (Max 51)',
          data: floorData,
          backgroundColor: barColors,
          borderRadius: 5,
          yAxisID: 'yFloor',
          order: 2
        },
        {
          label: 'Playtime (Seconds)',
          data: timeData,
          type: 'line',
          borderColor: '#22b8cf',
          backgroundColor: 'rgba(34, 184, 207, 0.15)',
          borderWidth: 2.5,
          pointRadius: 4,
          tension: 0.25,
          yAxisID: 'yTime',
          order: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        tooltip: {
          callbacks: {
            afterBody: function (items) {
              const idx = items[0].dataIndex;
              const r = DATA.runs[idx];
              return [
                `Phase: ${r.Phase}`,
                `Outcome: ${r.Outcome} (${r.Killed_By})`,
                `Playtime: ${r.Playtime_MMSS} (${r.Playtime_Sec}s)`,
                `Boss Relics: ${r.Boss_Relic_Act1}, ${r.Boss_Relic_Act2}`,
                `Score: ${r.Score}`
              ];
            }
          }
        }
      },
      scales: {
        yFloor: {
          type: 'linear',
          position: 'left',
          min: 0,
          max: 55,
          title: { display: true, text: 'Floor Reached' }
        },
        yTime: {
          type: 'linear',
          position: 'right',
          min: 0,
          grid: { drawOnChartArea: false },
          title: { display: true, text: 'Playtime (Seconds)' }
        }
      }
    }
  });

  // 2. Top 22 Cards by Times Picked & Pick Rate
  const topCards = DATA.cards.filter(c => c.Times_Offered >= 3).slice(0, 22);
  const cardCtx = document.getElementById('cardPickRateChart').getContext('2d');
  new Chart(cardCtx, {
    type: 'bar',
    data: {
      labels: topCards.map(c => c.Card_Name),
      datasets: [
        {
          label: 'Pick Rate (%)',
          data: topCards.map(c => c.Pick_Rate_Pct),
          backgroundColor: 'rgba(201, 42, 42, 0.82)',
          borderColor: '#ff6b6b',
          borderWidth: 1,
          borderRadius: 4
        },
        {
          label: 'Times Picked',
          data: topCards.map(c => c.Times_Picked),
          backgroundColor: 'rgba(245, 159, 0, 0.85)',
          borderRadius: 4
        },
        {
          label: 'Times Offered',
          data: topCards.map(c => c.Times_Offered),
          backgroundColor: 'rgba(156, 150, 168, 0.35)',
          borderRadius: 4
        }
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            afterBody: function (items) {
              const c = topCards[items[0].dataIndex];
              return `Bot Base Score: ${c.Bot_Base_Score} | Shop Buys: ${c.Shop_Purchases} | In Victory Deck: ${c.Copies_In_Victory_Deck}`;
            }
          }
        }
      }
    }
  });

  // 3. Relics Obtained Chart
  const topRelics = DATA.relics.filter(r => r.Relic_Name !== 'Burning Blood').slice(0, 18);
  const relicCtx = document.getElementById('relicsChart').getContext('2d');
  new Chart(relicCtx, {
    type: 'bar',
    data: {
      labels: topRelics.map(r => r.Relic_Name),
      datasets: [
        {
          label: 'Runs Obtained (out of 21)',
          data: topRelics.map(r => r.Runs_Obtained),
          backgroundColor: topRelics.map(r => r.In_Winning_Run === 'Yes' ? '#51cf66' : '#9775fa'),
          borderRadius: 4
        }
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        tooltip: {
          callbacks: {
            afterBody: function (items) {
              const r = topRelics[items[0].dataIndex];
              return `Presence: ${r.Run_Presence_Pct}% | Avg Floor: ${r.Avg_Floor_Obtained} | In Winning Run: ${r.In_Winning_Run}`;
            }
          }
        }
      }
    }
  });

  // 4. Winning Run #21 Floor-by-Floor Trajectory
  if (DATA.winning_run) {
    const wr = DATA.winning_run;
    const floors = wr.hp_per_floor.map((_, i) => `F${i + 1}`);
    const trajCtx = document.getElementById('winningRunTrajectoryChart').getContext('2d');
    new Chart(trajCtx, {
      type: 'line',
      data: {
        labels: floors,
        datasets: [
          {
            label: 'Current HP',
            data: wr.hp_per_floor,
            borderColor: '#51cf66',
            backgroundColor: 'rgba(81, 207, 102, 0.15)',
            fill: true,
            borderWidth: 2.5,
            pointRadius: 2.5,
            tension: 0.2,
            yAxisID: 'yHp'
          },
          {
            label: 'Max HP',
            data: wr.max_hp_per_floor,
            borderColor: '#ff6b6b',
            borderDash: [5, 4],
            borderWidth: 2,
            pointRadius: 0,
            yAxisID: 'yHp'
          },
          {
            label: 'Gold',
            data: wr.gold_per_floor,
            borderColor: '#ffd43b',
            borderWidth: 2,
            pointRadius: 2,
            tension: 0.2,
            yAxisID: 'yGold'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        scales: {
          yHp: {
            type: 'linear',
            position: 'left',
            min: 0,
            max: 105,
            title: { display: true, text: 'HP / Max HP' }
          },
          yGold: {
            type: 'linear',
            position: 'right',
            min: 0,
            grid: { drawOnChartArea: false },
            title: { display: true, text: 'Gold' }
          }
        }
      }
    });
  }

  // 5. Deadliest Enemy Encounters
  const topEnemies = [...DATA.enemies]
    .sort((a, b) => b.Avg_Damage_Taken - a.Avg_Damage_Taken)
    .slice(0, 14);
  const enemyCtx = document.getElementById('enemyDamageChart').getContext('2d');
  new Chart(enemyCtx, {
    type: 'bar',
    data: {
      labels: topEnemies.map(e => e.Enemy_Encounter),
      datasets: [
        {
          label: 'Avg HP Damage Taken',
          data: topEnemies.map(e => e.Avg_Damage_Taken),
          backgroundColor: 'rgba(224, 49, 49, 0.8)',
          borderRadius: 4
        },
        {
          label: 'Avg Turns',
          data: topEnemies.map(e => e.Avg_Turns),
          backgroundColor: 'rgba(34, 184, 207, 0.75)',
          borderRadius: 4
        }
      ]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false
    }
  });

  // Render Iteration Timeline
  const timelineContainer = document.getElementById('timeline-container');
  DATA.iterations.forEach(it => {
    const isVic = it.runs.includes('VICTORY');
    const div = document.createElement('div');
    div.className = 'timeline-item' + (isVic ? ' victory-item' : '');
    div.innerHTML = `
      <div class="timeline-meta">
        <div class="iter-tag">${it.iteration}</div>
        <div class="iter-runs">${it.runs}</div>
        <span class="iter-floor">Peak Floor: ${it.floor_peak}</span>
      </div>
      <div class="timeline-body">
        <h4>${it.phase} <small style="color:#9c96a8;font-weight:400;">(${it.files_modified})</small></h4>
        <div class="issue"><strong>Observed Bottleneck:</strong> ${it.issue_observed}</div>
        <div class="fix"><strong>Strategy &amp; Code Fix:</strong> ${it.strategy_change}</div>
      </div>
    `;
    timelineContainer.appendChild(div);
  });

  // Interactive Spreadsheet Viewer
  const sheetsMap = {
    runs: DATA.runs,
    cards: DATA.cards,
    relics: DATA.relics,
    iterations: DATA.iterations,
    enemies: DATA.enemies,
    combats: DATA.combats
  };

  let currentSheetKey = 'runs';
  let sortCol = null;
  let sortAsc = true;
  let searchQuery = '';

  const thead = document.getElementById('table-head');
  const tbody = document.getElementById('table-body');
  const searchInput = document.getElementById('table-search');

  function getFilteredRows() {
    let rows = [...(sheetsMap[currentSheetKey] || [])];
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      rows = rows.filter(r => Object.values(r).some(v => String(v).toLowerCase().includes(q)));
    }
    if (sortCol) {
      rows.sort((a, b) => {
        const va = a[sortCol];
        const vb = b[sortCol];
        if (typeof va === 'number' && typeof vb === 'number') {
          return sortAsc ? va - vb : vb - va;
        }
        return sortAsc
          ? String(va).localeCompare(String(vb))
          : String(vb).localeCompare(String(va));
      });
    }
    return rows;
  }

  function renderTable() {
    const baseRows = sheetsMap[currentSheetKey] || [];
    if (!baseRows.length) return;
    const headers = Object.keys(baseRows[0]);

    thead.innerHTML = '';
    const trHead = document.createElement('tr');
    headers.forEach(h => {
      const th = document.createElement('th');
      const arrow = sortCol === h ? (sortAsc ? ' ▲' : ' ▼') : '';
      th.textContent = h.replace(/_/g, ' ') + arrow;
      th.addEventListener('click', () => {
        if (sortCol === h) sortAsc = !sortAsc;
        else { sortCol = h; sortAsc = false; }
        renderTable();
      });
      trHead.appendChild(th);
    });
    thead.appendChild(trHead);

    const rows = getFilteredRows();
    tbody.innerHTML = '';
    rows.forEach(r => {
      const tr = document.createElement('tr');
      if (r.Outcome === 'VICTORY' || r.In_Winning_Run === 'Yes' || (r.runs && r.runs.includes('VICTORY'))) {
        tr.className = 'victory-row';
      }
      headers.forEach(h => {
        const td = document.createElement('td');
        td.textContent = r[h] !== undefined && r[h] !== null ? r[h] : '';
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
  }

  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentSheetKey = btn.getAttribute('data-sheet');
      sortCol = null;
      renderTable();
    });
  });

  searchInput.addEventListener('input', e => {
    searchQuery = e.target.value;
    renderTable();
  });

  // Copy TSV for Google Sheets
  document.getElementById('copy-tsv-btn').addEventListener('click', () => {
    const rows = getFilteredRows();
    if (!rows.length) return;
    const headers = Object.keys(rows[0]);
    const lines = [headers.join('\t')];
    rows.forEach(r => {
      lines.push(headers.map(h => String(r[h] ?? '').replace(/\t|\n/g, ' ')).join('\t'));
    });
    navigator.clipboard.writeText(lines.join('\n')).then(() => {
      const toast = document.getElementById('toast');
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2800);
    });
  });

  renderTable();
})();
