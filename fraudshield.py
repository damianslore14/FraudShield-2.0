"""FraudShield 2.0 - desktop transaction-monitoring educational prototype."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path

import database
from risk_engine import assess_transaction
from analytics import summarize, level_distribution, hourly_distribution
from reports import export_csv
from fraud_model import detect_anomalies

BG = "#0B1120"
SIDEBAR = "#101A2B"
PANEL = "#162338"
PANEL_LIGHT = "#1D2D45"
WHITE = "#F1F5F9"
MUTED = "#91A3B8"
BLUE = "#38BDF8"
GREEN = "#34D399"
YELLOW = "#FBBF24"
RED = "#FB7185"
PURPLE = "#A78BFA"

SEED_DATA = [
    {"id": "TX001", "customer": "C001", "amount": 250, "country": "PE", "hour": 14, "channel": "APP"},
    {"id": "TX002", "customer": "C002", "amount": 7500, "country": "PE", "hour": 10, "channel": "WEB"},
    {"id": "TX003", "customer": "C003", "amount": 1200, "country": "XX", "hour": 2, "channel": "WEB"},
    {"id": "TX004", "customer": "C004", "amount": 9000, "country": "XX", "hour": 23, "channel": "APP"},
    {"id": "TX005", "customer": "C005", "amount": 80, "country": "PE", "hour": 9, "channel": "AGENCY"},
    {"id": "TX006", "customer": "C006", "amount": 6000, "country": "PE", "hour": 3, "channel": "APP"},
    {"id": "TX007", "customer": "C007", "amount": 450, "country": "PE", "hour": 15, "channel": "WEB"},
    {"id": "TX008", "customer": "C008", "amount": 11000, "country": "XX", "hour": 1, "channel": "APP"},
    {"id": "TX009", "customer": "C009", "amount": 320, "country": "PE", "hour": 20, "channel": "AGENCY"},
    {"id": "TX010", "customer": "C010", "amount": 850, "country": "PE", "hour": 12, "channel": "WEB"},
]


class FraudShieldApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FraudShield 2.0 | Risk Intelligence")
        self.root.geometry("1320x850")
        self.root.minsize(1080, 700)
        self.root.configure(bg=BG)
        self.threshold = tk.DoubleVar(value=5000)
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="ALL")
        self.records = []
        self._configure_style()
        database.initialize(SEED_DATA)
        self._build_layout()
        self.refresh_analysis()

    def _configure_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=PANEL, foreground=WHITE, fieldbackground=PANEL,
                        rowheight=32, borderwidth=0, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background=SIDEBAR, foreground=BLUE,
                        font=("Segoe UI", 9, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#294665")], foreground=[("selected", WHITE)])
        style.configure("TCombobox", fieldbackground=PANEL_LIGHT, background=PANEL_LIGHT,
                        foreground=WHITE, arrowcolor=BLUE)

    def _label(self, parent, text, size=10, color=WHITE, bold=False, **kwargs):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=("Segoe UI", size, "bold" if bold else "normal"), **kwargs)

    def _button(self, parent, text, command, color=BLUE, fg=BG):
        return tk.Button(parent, text=text, command=command, bg=color, fg=fg,
                         activebackground=color, activeforeground=fg, relief="flat",
                         cursor="hand2", font=("Segoe UI", 9, "bold"), padx=12, pady=8)

    def _build_layout(self):
        shell = tk.Frame(self.root, bg=BG)
        shell.pack(fill="both", expand=True)
        sidebar = tk.Frame(shell, bg=SIDEBAR, width=215)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        self._label(sidebar, "◈ FRAUDSHIELD", 17, BLUE, True).pack(anchor="w", padx=18, pady=(28, 4))
        self._label(sidebar, "RISK INTELLIGENCE 2.0", 8, MUTED, True).pack(anchor="w", padx=20, pady=(0, 32))
        for title in ("MAIN MENU", "▦  Dashboard", "◉  Transactions", "⚠  Risk alerts", "◈  Analytics", "▤  Reports"):
            self._label(sidebar, title, 9 if title == "MAIN MENU" else 10,
                        MUTED if title == "MAIN MENU" else WHITE, title == "MAIN MENU").pack(anchor="w", padx=20, pady=10)
        tk.Frame(sidebar, bg=PANEL_LIGHT, height=1).pack(fill="x", padx=16, pady=20)
        self._label(sidebar, "●  DATABASE CONNECTED", 8, GREEN, True).pack(anchor="w", padx=18)
        self._label(sidebar, "SQLite local storage", 8, MUTED).pack(anchor="w", padx=18, pady=6)

        self.content = tk.Frame(shell, bg=BG)
        self.content.pack(side="left", fill="both", expand=True, padx=22, pady=18)
        self._build_header()
        self._build_metrics()
        self._build_controls()
        self._build_table()
        self._build_bottom_panels()
        self._build_footer()

    def _build_header(self):
        row = tk.Frame(self.content, bg=BG)
        row.pack(fill="x", pady=(0, 16))
        left = tk.Frame(row, bg=BG); left.pack(side="left")
        self._label(left, "Transaction Monitoring", 20, WHITE, True).pack(anchor="w")
        self._label(left, "Financial risk detection, explainable alerts and analytics", 9, MUTED).pack(anchor="w", pady=3)
        right = tk.Frame(row, bg=BG); right.pack(side="right")
        self._label(right, "● SYSTEM ONLINE", 9, GREEN, True).pack(anchor="e")
        self._label(right, datetime.now().strftime("%d/%m/%Y"), 9, MUTED).pack(anchor="e", pady=3)

    def _build_metrics(self):
        frame = tk.Frame(self.content, bg=BG); frame.pack(fill="x", pady=(0, 14))
        self.metric_values = {}
        for title, key, color in [("TOTAL TRANSACTIONS", "total", BLUE), ("GENERATED ALERTS", "alerts", YELLOW),
                                  ("HIGH RISK", "high", RED), ("LOW RISK", "low", GREEN)]:
            card = tk.Frame(frame, bg=PANEL, padx=14, pady=12); card.pack(side="left", fill="both", expand=True, padx=4)
            self._label(card, title, 8, MUTED, True).pack(anchor="w")
            value = tk.Label(card, text="0", bg=PANEL, fg=color, font=("Segoe UI", 24, "bold"))
            value.pack(anchor="w", pady=(5, 0)); self.metric_values[key] = value

    def _build_controls(self):
        actions = tk.Frame(self.content, bg=BG); actions.pack(fill="x", pady=(0, 10))
        self._label(actions, "TRANSACTION ANALYSIS", 11, WHITE, True).pack(side="left")
        self._button(actions, "+ NEW TRANSACTION", self.add_transaction, PURPLE, WHITE).pack(side="right", padx=3)
        self._button(actions, "ANALYTICS CHARTS", self.show_charts, "#334155", WHITE).pack(side="right", padx=3)
        self._button(actions, "ML ANOMALIES", self.run_ml, "#334155", WHITE).pack(side="right", padx=3)
        self._button(actions, "EXPORT CSV", self.save_report, GREEN).pack(side="right", padx=3)
        self._button(actions, "ANALYZE", self.refresh_analysis).pack(side="right", padx=3)

        filters = tk.Frame(self.content, bg=BG); filters.pack(fill="x", pady=(0, 10))
        tk.Entry(filters, textvariable=self.search_var, bg=PANEL_LIGHT, fg=WHITE, insertbackground=WHITE,
                 relief="flat", font=("Segoe UI", 9), width=20).pack(side="left", ipady=7)
        self.search_var.trace_add("write", lambda *_: self.render_table())
        ttk.Combobox(filters, textvariable=self.filter_var, values=["ALL", "HIGH", "MEDIUM", "LOW"],
                     state="readonly", width=10).pack(side="left", padx=8, ipady=4)
        self.filter_var.trace_add("write", lambda *_: self.render_table())
        self._label(filters, "Amount threshold (S/):", 9, MUTED).pack(side="left", padx=(15, 5))
        tk.Spinbox(filters, from_=500, to=50000, increment=500, textvariable=self.threshold, width=9,
                   bg=PANEL_LIGHT, fg=WHITE, buttonbackground=PANEL_LIGHT, relief="flat",
                   font=("Segoe UI", 9)).pack(side="left", ipady=5)

    def _build_table(self):
        wrapper = tk.Frame(self.content, bg=PANEL, padx=8, pady=8); wrapper.pack(fill="both", expand=True)
        cols = ("id", "customer", "amount", "country", "hour", "channel", "score", "level", "reason")
        self.table = ttk.Treeview(wrapper, columns=cols, show="headings")
        headers = {"id":"TRANSACTION ID", "customer":"CUSTOMER", "amount":"AMOUNT (S/)", "country":"COUNTRY",
                   "hour":"HOUR", "channel":"CHANNEL", "score":"SCORE", "level":"RISK", "reason":"INDICATORS"}
        widths = {"id":100, "customer":85, "amount":100, "country":70, "hour":65, "channel":80, "score":55, "level":80, "reason":300}
        for col in cols:
            self.table.heading(col, text=headers[col]); self.table.column(col, width=widths[col], anchor="w" if col == "reason" else "center")
        for level, color in [("HIGH", RED), ("MEDIUM", YELLOW), ("LOW", GREEN)]:
            self.table.tag_configure(level, foreground=color)
        scroll = ttk.Scrollbar(wrapper, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        self.table.bind("<<TreeviewSelect>>", self.show_details)

    def _build_bottom_panels(self):
        row = tk.Frame(self.content, bg=BG); row.pack(fill="x", pady=10)
        self.details = tk.Label(row, text="Select a transaction to inspect its risk indicators.", bg=PANEL,
                                fg=MUTED, font=("Segoe UI", 9), justify="left", anchor="w", padx=12, pady=10)
        self.details.pack(fill="x")
        self.analytics_text = tk.Label(row, text="", bg=BG, fg=BLUE, font=("Segoe UI", 9), anchor="w")
        self.analytics_text.pack(fill="x", pady=(8, 0))

    def _build_footer(self):
        footer = tk.Frame(self.content, bg=BG); footer.pack(fill="x", pady=(4, 0))
        self.status = tk.Label(footer, text="FraudShield 2.0 | Synthetic data | Educational prototype", bg=BG, fg=MUTED, font=("Segoe UI", 8))
        self.status.pack(side="left")
        self._label(footer, "ALERTS REQUIRE HUMAN REVIEW — NOT PROOF OF FRAUD", 8, YELLOW, True).pack(side="right")

    def refresh_analysis(self):
        try:
            threshold = float(self.threshold.get())
            if threshold <= 0: raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Invalid threshold", "Enter a positive amount threshold."); return
        raw = database.get_transactions()
        self.records = []
        for tx in raw:
            result = assess_transaction(tx, threshold)
            self.records.append({**tx, "score": result.score, "level": result.level, "reasons": result.reasons})
        stats = summarize(self.records)
        for key in ("total", "alerts", "high", "low"):
            self.metric_values[key].config(text=str(stats[key]))
        self.render_table()
        self.analytics_text.config(text=(f"Analytics  |  Medium: {stats['medium']}   •   Alert rate: {stats['alert_rate']:.1f}%"
                                         f"   •   Total volume: S/ {stats['amount_total']:,.2f}"))
        self.status.config(text=f"Last analysis: {datetime.now().strftime('%H:%M:%S')} | {len(self.records)} records loaded from SQLite")

    def render_table(self):
        for item in self.table.get_children(): self.table.delete(item)
        query = self.search_var.get().strip().lower()
        level = self.filter_var.get()
        for r in self.records:
            if level != "ALL" and r["level"] != level: continue
            if query and query not in r["id"].lower() and query not in r["customer"].lower(): continue
            reason = "; ".join(r["reasons"]) if r["reasons"] else "No rule indicators"
            self.table.insert("", "end", values=(r["id"], r["customer"], f"{r['amount']:,.2f}", r["country"],
                              f"{int(r['hour']):02d}:00", r["channel"], r["score"], r["level"], reason), tags=(r["level"],))

    def show_details(self, _event=None):
        selected = self.table.selection()
        if not selected: return
        tx_id = self.table.item(selected[0], "values")[0]
        record = next((r for r in self.records if r["id"] == tx_id), None)
        if record:
            reason = "; ".join(record["reasons"]) if record["reasons"] else "No indicators under current rules."
            self.details.config(text=f"{record['id']}  |  Customer {record['customer']}  |  S/ {record['amount']:,.2f}  |  {record['level']} ({record['score']} points)  |  {reason}")

    def add_transaction(self):
        win = tk.Toplevel(self.root); win.title("Register transaction"); win.geometry("390x500")
        win.configure(bg=SIDEBAR); win.transient(self.root); win.grab_set()
        self._label(win, "REGISTER TRANSACTION", 15, BLUE, True).pack(pady=16)
        fields = {}
        for label, key, default in [("Transaction ID", "id", "TX011"), ("Customer ID", "customer", "C011"),
                                    ("Amount (S/)", "amount", "500"), ("Country code", "country", "PE"),
                                    ("Hour (0-23)", "hour", "12"), ("Channel (APP/WEB/AGENCY)", "channel", "APP")]:
            self._label(win, label, 9, MUTED).pack(anchor="w", padx=35, pady=(5, 2))
            entry = tk.Entry(win, bg=PANEL_LIGHT, fg=WHITE, insertbackground=WHITE, relief="flat", font=("Segoe UI", 10))
            entry.pack(fill="x", padx=35, ipady=7); entry.insert(0, default); fields[key] = entry

        def save():
            try:
                tx = {key: entry.get().strip() for key, entry in fields.items()}
                tx["amount"] = float(tx["amount"]); tx["hour"] = int(tx["hour"])
                tx["country"] = tx["country"].upper(); tx["channel"] = tx["channel"].upper()
                if not tx["id"] or not tx["customer"]: raise ValueError("IDs cannot be empty.")
                if tx["amount"] <= 0: raise ValueError("Amount must be greater than zero.")
                if not 0 <= tx["hour"] <= 23: raise ValueError("Hour must be between 0 and 23.")
                if len(tx["country"]) != 2 or not tx["country"].isalpha(): raise ValueError("Country must be a two-letter code.")
                if tx["channel"] not in {"APP", "WEB", "AGENCY"}: raise ValueError("Channel must be APP, WEB or AGENCY.")
                database.add_transaction(tx)
                win.destroy(); self.refresh_analysis()
                messagebox.showinfo("Saved", "Transaction saved to the local SQLite database.")
            except ValueError as exc: messagebox.showerror("Invalid data", str(exc))
            except Exception as exc: messagebox.showerror("Could not save", str(exc))
        self._button(win, "SAVE TRANSACTION", save, GREEN).pack(pady=18)

    def save_report(self):
        if not self.records:
            messagebox.showinfo("No records", "There are no records to export."); return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile="FraudShield_Report.csv")
        if not path: return
        try:
            export_csv(self.records, path)
            messagebox.showinfo("Export complete", f"Report saved to:\n{path}")
        except OSError as exc: messagebox.showerror("Export error", str(exc))

    def show_charts(self):
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        except ImportError:
            messagebox.showwarning("Charts unavailable", "Install matplotlib with: python -m pip install matplotlib")
            return
        if not self.records:
            messagebox.showinfo("No data", "There are no analyzed records to chart.")
            return
        distribution = level_distribution(self.records)
        hourly = hourly_distribution(self.records)
        win = tk.Toplevel(self.root)
        win.title("FraudShield | Analytics")
        win.geometry("950x570")
        win.configure(bg=BG)
        figure = Figure(figsize=(9, 5), dpi=100, facecolor=BG)
        ax1 = figure.add_subplot(121)
        ax1.set_facecolor(PANEL)
        labels = [k for k, v in distribution.items() if v > 0]
        values = [v for v in distribution.values() if v > 0]
        colors = {"LOW": GREEN, "MEDIUM": YELLOW, "HIGH": RED}
        if values:
            ax1.pie(values, labels=labels, autopct="%1.0f%%", startangle=90,
                    colors=[colors[k] for k in labels], textprops={"color": WHITE})
        ax1.set_title("Risk level distribution", color=WHITE, pad=15)
        ax2 = figure.add_subplot(122)
        ax2.set_facecolor(PANEL)
        ax2.bar(list(hourly.keys()), list(hourly.values()), color=BLUE)
        ax2.set_title("Transactions by hour", color=WHITE, pad=15)
        ax2.set_xlabel("Hour", color=WHITE)
        ax2.set_ylabel("Transactions", color=WHITE)
        ax2.tick_params(colors=WHITE)
        for spine in ax2.spines.values(): spine.set_color(MUTED)
        figure.tight_layout(pad=3)
        canvas = FigureCanvasTkAgg(figure, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def run_ml(self):
        try:
            findings = detect_anomalies(self.records)
        except (ValueError, RuntimeError) as exc:
            messagebox.showwarning("Experimental model", str(exc)); return
        lines = [f"{r['id']}: {r['model_result']} (score {r['anomaly_score']})" for r in findings]
        messagebox.showinfo("Isolation Forest — experimental", "\n".join(lines) +
                            "\n\nThis unsupervised model flags unusual patterns, not confirmed fraud.")


def main():
    root = tk.Tk()
    FraudShieldApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
