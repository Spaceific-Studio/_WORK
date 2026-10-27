from datetime import datetime, timedelta
import win32com.client

CATEGORY_NAME = "HOMEOFFICE"


def get_calendar_folder():
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")

    # 9 = olFolderCalendar
    return namespace.GetDefaultFolder(9)


def get_week_range():
    today = datetime.today()

    monday = today - timedelta(days=today.weekday())
    monday = monday.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    next_monday = monday + timedelta(days=7)

    return monday, next_monday


def load_homeoffice_events():
    calendar = get_calendar_folder()

    items = calendar.Items

    items.Sort("[Start]")
    items.IncludeRecurrences = True

    monday, next_monday = get_week_range()

    restriction = (
        "[Start] >= '"
        + monday.strftime("%d.%m.%Y %H:%M")
        + "' AND [Start] < '"
        + next_monday.strftime("%d.%m.%Y %H:%M")
        + "'"
    )

    print("=" * 80)
    print("RESTRICTION")
    print(restriction)
    print("=" * 80)

    filtered_items = items.Restrict(restriction)

    result = []

    for event in filtered_items:

        try:

            categories = str(event.Categories or "")

            if CATEGORY_NAME.upper() not in categories.upper():
                continue

            item = {
                "subject": str(event.Subject),
                "start": event.Start,
                "end": event.End,
                "categories": categories,
                "all_day": bool(event.AllDayEvent),
            }

            result.append(item)

        except Exception as exc:
            print(f"CHYBA U POLOŽKY: {exc}")

    return result


def print_events(events):

    print()
    print("=" * 80)
    print(f"NALEZENO {len(events)} HOME OFFICE UDÁLOSTÍ")
    print("=" * 80)

    for i, event in enumerate(events, start=1):

        print()
        print(f"[{i}]")
        print("Předmět :", event["subject"])
        print("Začátek :", event["start"])
        print("Konec   :", event["end"])
        print("Kategorie:", event["categories"])
        print("Celodenní:", event["all_day"])


if __name__ == "__main__":

    events = load_homeoffice_events()

    print_events(events)