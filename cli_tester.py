import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from core.database import db
from core.coach_engine import coach_engine

console = Console()

def display_tactical_board(result):
    stats = result.get("combo_stats")
    if not stats:
        part = result.get("part_info")
        if part:
            table = Table(title=f"【部件檔案庫】{part.get('name')} {part.get('name_zh', '')}", box=box.ROUNDED)
            table.add_column("屬性", style="cyan")
            table.add_column("規格數值", style="green")
            table.add_row("類別", part.get("_category", "零件"))
            table.add_row("淨重", f"約 {part.get('weight_g')}g")
            table.add_row("評定階級", part.get("tier", "A"))
            table.add_row("官方圖片 URL", part.get("image_url", "N/A"))
            console.print(table)
        return

    scores = stats["scores"]
    b = stats["blade"]
    r = stats["ratchet"]
    bit = stats["bit"]

    # Table of 4-dimension scores
    score_table = Table(title="[bold yellow]★ BEYBLADE X 職業聯賽四維戰力遙測 ★[/bold yellow]", box=box.HEAVY_EDGE)
    score_table.add_column("戰術維度", style="bold cyan", width=18)
    score_table.add_column("評分", justify="center", width=8)
    score_table.add_column("戰術能量條 (Progress)", width=32)

    def bar(val, color):
        filled = int(val / 100 * 25)
        empty = 25 - filled
        return f"[{color}]{'█' * filled}[/{color}][dim]{'░' * empty}[/dim]"

    score_table.add_row("一、攻擊破壞力", f"{scores['attack']}/100", bar(scores['attack'], "red"))
    score_table.add_row("二、極致持久力", f"{scores['stamina']}/100", bar(scores['stamina'], "green"))
    score_table.add_row("三、防禦抗爆力", f"{scores['defense']}/100", bar(scores['defense'], "blue"))
    score_table.add_row("四、X-Dash 突襲率", f"{scores['xdash']}/100", bar(scores['xdash'], "yellow"))

    console.print(score_table)

    # Component specs
    comp_panel = (
        f"[bold white]搭配名稱：[/bold white] [bold magenta]{stats['combo_name']}[/bold magenta] ({stats['combo_name_zh']})\n"
        f"[bold white]物理總重：[/bold white] [bold yellow]{stats['total_weight_g']}g[/bold yellow] (聯賽 S 階配重標竿)\n"
        f"[bold white]刃 (Blade)：[/bold white] {b['name']} ({b['name_zh']}) [{b['weight_g']}g] | 重心: {b['cg']}\n"
        f"[bold white]墊片 (Ratchet)：[/bold white] {r['name']} [{r['weight_g']}g] | 高度: {r['height_mm']}mm | {r['blades_count']}齒抗爆\n"
        f"[bold white]軸點 (Bit)：[/bold white] {bit['name']} [{bit['weight_g']}g] | {bit['gear_teeth']} 齒輪 X-Line 咬合\n"
        f"[bold cyan]參考圖片 URL：[/bold cyan] {stats['hero_image_url']}"
    )
    console.print(Panel(comp_panel, title="[bold green]實體裝配數據[/bold green]", box=box.ROUNDED))

def main():
    console.print(Panel(
        "[bold cyan]全球頂尖《戰鬥陀螺 X》(Beyblade X) 職業聯賽戰術教練終端[/bold cyan]\n"
        "[dim]支援完整 BX/UX 部件即時拆解、四維雷達數值運算與官方圖片對照[/dim]\n"
        "請輸入搭配（例如：[bold yellow]Phoenix Wing 9-60O[/bold yellow]、[bold yellow]魔導權杖 7-60B[/bold yellow]、[bold yellow]Dran Buster 1-60F[/bold yellow]）或輸入 [bold red]quit[/bold red] 結束。",
        title="[bold red]X 競技場整備區已就緒[/bold red]",
        box=box.DOUBLE
    ))

    while True:
        try:
            user_input = console.input("\n[bold green]選手提問 > [/bold green]").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit", "q"]:
                console.print("[dim]教練退出整備區，預祝世界大賽奪冠！[/dim]")
                break

            with console.status("[bold cyan]戰術大腦運算中...[/bold cyan]", spinner="dots"):
                result = coach_engine.analyze(user_input)

            display_tactical_board(result)
            
            reply = result.get("reply_text", "")
            console.print(Panel(reply, title="[bold yellow]教練深度戰術點評[/bold yellow]", border_style="yellow"))

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]錯誤：[/bold red]{e}")

if __name__ == "__main__":
    main()
