import sys
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import create_app  # noqa: E402
from app.services.statistics_service import StatisticsService  # noqa: E402


def export_excel(month: str | None, output_path: Path):
    app = create_app("development")
    with app.app_context():
        report = StatisticsService.month_summary(month)

        wb = Workbook()
        ws = wb.active
        ws.title = "Attendance"
        ws.append(["user_id", "name", "department", "total", "normal", "late"])
        for item in report["items"]:
            ws.append(
                [
                    item["user_id"],
                    item["name"],
                    item["department"],
                    item["total"],
                    item["normal"],
                    item["late"],
                ]
            )
        wb.save(output_path)
        print(f"exported to {output_path}")


if __name__ == "__main__":
    month_arg = sys.argv[1] if len(sys.argv) > 1 else None
    output = ROOT / "attendance_report.xlsx"
    export_excel(month_arg, output)
