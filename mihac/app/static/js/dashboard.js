// ============================================================
// MIHAC v1.0 — dashboard.js
// Gráficas del Dashboard con Chart.js 4.4
// ============================================================

document.addEventListener("DOMContentLoaded", () => {

    // ── Helpers ─────────────────────────────────────────────
    function getData(id) {
        const el = document.getElementById(id);
        if (!el) return null;
        try {
            return JSON.parse(el.textContent);
        } catch (e) {
            console.error("Error parsing", id, e);
            return null;
        }
    }

    // Defaults globales de Chart.js
    Chart.defaults.font.family = "'Inter', sans-serif";
    Chart.defaults.font.size = 13;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;

    // ── 1. Pie Chart: Dictámenes ────────────────────────────
    const dictData = getData("dataDictamen");
    if (dictData) {
        const ctx = document.getElementById("chartDictamen");
        if (ctx) {
            new Chart(ctx, {
                type: "pie",
                data: {
                    labels: dictData.labels,
                    datasets: [{
                        data: dictData.data,
                        backgroundColor: dictData.colors,
                        borderWidth: 2,
                        borderColor: "#ffffff",
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: { padding: 16 },
                        },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => {
                                    const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                    const pct = total > 0
                                        ? ((ctx.parsed / total) * 100).toFixed(1)
                                        : "0.0";
                                    return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    // ── 2. Bar Chart: Histograma de Scores ──────────────────
    const scoreData = getData("dataScores");
    if (scoreData) {
        const ctx = document.getElementById("chartScores");
        if (ctx) {
            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: scoreData.labels,
                    datasets: [{
                        label: "Evaluaciones",
                        data: scoreData.data,
                        backgroundColor: scoreData.colors,
                        borderRadius: 6,
                        borderSkipped: false,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1, precision: 0 },
                            grid: { color: "rgba(0,0,0,0.05)" },
                        },
                        x: {
                            grid: { display: false },
                        }
                    }
                }
            });
        }
    }

    // ── 3. Doughnut Chart: DTI ──────────────────────────────
    const dtiData = getData("dataDTI");
    if (dtiData) {
        const ctx = document.getElementById("chartDTI");
        if (ctx) {
            new Chart(ctx, {
                type: "doughnut",
                data: {
                    labels: dtiData.labels,
                    datasets: [{
                        data: dtiData.data,
                        backgroundColor: dtiData.colors,
                        borderWidth: 2,
                        borderColor: "#ffffff",
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    cutout: "55%",
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: { padding: 12, font: { size: 11 } },
                        },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => {
                                    const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                    const pct = total > 0
                                        ? ((ctx.parsed / total) * 100).toFixed(1)
                                        : "0.0";
                                    return ` ${ctx.label}: ${ctx.parsed} (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    // ── 4. Horizontal Bar: Propósitos ───────────────────────
    const propData = getData("dataProposito");
    if (propData) {
        const ctx = document.getElementById("chartProposito");
        if (ctx) {
            // Colores por propósito
            const propColors = {
                "Negocio":    "#1B4F8A",
                "Educacion":  "#0E7C7B",
                "Consumo":    "#17BEBB",
                "Emergencia": "#F59E0B",
                "Vacaciones": "#64748B",
            };
            const colors = propData.labels.map(
                (l) => propColors[l] || "#94A3B8"
            );

            new Chart(ctx, {
                type: "bar",
                data: {
                    labels: propData.labels,
                    datasets: [{
                        label: "Evaluaciones",
                        data: propData.data,
                        backgroundColor: colors,
                        borderRadius: 6,
                        borderSkipped: false,
                    }]
                },
                options: {
                    indexAxis: "y",
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: { display: false },
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            ticks: { stepSize: 1, precision: 0 },
                            grid: { color: "rgba(0,0,0,0.05)" },
                        },
                        y: {
                            grid: { display: false },
                        }
                    }
                }
            });
        }
    }

});
