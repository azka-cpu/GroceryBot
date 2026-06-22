import os
from langchain_core.tools import tool
from db.database import get_session
from db.crud import (
    get_slip_summary,
    get_item_history,
    compare_two_months,
    get_monthly_totals,
)
@tool
def get_all_slips_summary(user_id: str) -> str:
    """Get overview of all grocery slips for a user."""
    user_id = int(user_id)
    session = get_session()
    try:
        slips = get_slip_summary(session, user_id)
        if not slips:
            return "No slips found. Please upload your grocery slip photos first."

        lines = ["Your Grocery Slips:", "-" * 50]
        grand_total = 0.0

        for s in slips:
            lines.append(
                f" {s['month']} | {s['store']:<15} | Rs.{s['total']:>8.2f} | {s['item_count']} items"
            )
            grand_total += s['total']

        lines.append("-" * 50)
        lines.append(f" Grand Total: Rs.{grand_total:.2f}")
        return "\n".join(lines)
    except Exception as e:
        return f"Something went wrong: {e}"
    finally:
        session.close()
@tool
def get_item_price_history(user_id: int, item_name: str) -> str:
    """Get price history of a specific grocery item across all months."""
    user_id = int(user_id)
    session = get_session()
    try:
        items = get_item_history(session, user_id, item_name)
        if not items:
            return f"No records found for '{item_name}'."

        lines = [f"Price History for '{item_name}'", "-" * 50]
        for it in items:
            lines.append(
                f" {it['month']} | {it['quantity']}{it['unit']} | "
                f"Rs.{it['unit_price']}/{it['unit']} | Total: Rs.{it['total_price']}"
            )
        prices = [it['unit_price'] for it in items]
        if len(prices) > 1:
            change = prices[-1] - prices[0]
            pct = (change / prices[0] * 100) if prices[0] else 0
            trend = "gone up" if change > 0 else "gone down"
            lines.append("-" * 50)
            lines.append(f" Price has {trend} by Rs.{abs(change):.2f} ({abs(pct):.1f}%)")

        return "\n".join(lines)
    except Exception as e:
        return f"Something went wrong: {e}"
    finally:
        session.close()

@tool
def compare_two_months_tool(user_id: int, month1: str, month2: str) -> str:
    """Compare grocery spending between two months. Use YYYY-MM format for months."""
    user_id = int(user_id)
    session = get_session()
    try:
        data = compare_two_months(session, user_id, month1, month2)
        if "error" in data:
            return data["error"]

        diff = data["total_change"]
        pct = data["total_pct_change"]
        spent_more = diff > 0
        lines = [
            f"{month1} vs {month2}",
            "-" * 55,
            f" {month1}: Rs.{data['total1']:.2f}",
            f" {month2}: Rs.{data['total2']:.2f}",
            f" You spent {'more' if spent_more else 'less'} in {month2} — Rs.{abs(diff):.2f} ({abs(pct):.1f}%)",
            "\n Item breakdown:",
        ]
        for item in data["item_comparison"]:
            p1 = f"Rs.{item['month1_price']:.2f}" if item["month1_price"] else "N/A"
            p2 = f"Rs.{item['month2_price']:.2f}" if item["month2_price"] else "N/A"
            change_val = item.get("change", 0)
            if change_val:
                ch = f"{'up' if change_val > 0 else 'down'} Rs.{abs(change_val):.2f}"
            else:
                ch = item.get("status", "")
            lines.append(f" {item['name']:<18} {p1:>10} -> {p2:>10} ({ch})")
        return "\n".join(lines)
    except Exception as e:
        return f"Something went wrong: {e}"
    finally:
        session.close()
@tool
def get_spending_trend(user_id: int) -> str:
    """Get monthly spending trend for a user."""
    user_id = int(user_id)
    session = get_session()
    try:
        totals = get_monthly_totals(session, user_id)
        if not totals:
            return "No spending data available yet."

        lines = ["Monthly Spending Trend", "-" * 35]
        highest = max(t["total"] for t in totals)

        for t in totals:
            bar = "" * int((t["total"] / highest) * 20)
            lines.append(f" {t['month']} Rs.{t['total']:>8.2f} {bar}")

        avg = sum(t["total"] for t in totals) / len(totals)
        total_all = sum(t["total"] for t in totals)
        lines += [
            "-" * 35,
            f" Monthly avg : Rs.{avg:.2f}",
            f" Total spent : Rs.{total_all:.2f}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"Something went wrong: {e}"
    finally:
        session.close()
@tool
def calculator(expression: str) -> str:
    """Evaluate a basic math expression. Example: 150 * 3 + 200"""
    try:
        allowed = set("0123456789+-*/(). ")
        if not all(c in allowed for c in expression):
            return "Only numbers and basic operators are allowed: + - * / ( )"
        result = eval(expression)
        return f"{expression} = {round(result, 4)}"
    except ZeroDivisionError:
        return "Cannot divide by zero."
    except Exception as e:
        return f"Could not calculate: {e}"
@tool
def search_market_price(item_name: str, user_id: str) -> str:
    """Search current market price of a grocery item online."""
    user_id = int(user_id)
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        results = client.search(
            f"today market price {item_name} per kg Pakistan 2026",
            max_results=2
        )
        lines = [f"Market Price: {item_name}", "-" * 50]
        for r in results.get("results", [])[:2]:
            snippet = r.get("content", "")[:200]
            lines.append(f" {snippet}...")
            lines.append(f" Source: {r.get('url', '')}\n")

        session = get_session()
        try:
            history = get_item_history(session, user_id, item_name)
            if history:
                lines.append(" What you paid recently:")
                for it in history[-3:]:
                    lines.append(f" {it['month']}: Rs.{it['unit_price']}/{it['unit']}")
        finally:
            session.close()

        return "\n".join(lines)
    except Exception as e:
        return f"Search failed: {e}"
ALL_TOOLS = [
    get_all_slips_summary,
    get_item_price_history,
    compare_two_months_tool,
    get_spending_trend,
    calculator,
    search_market_price,
]