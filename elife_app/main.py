from datetime import date
from elife_app.data_access.db import create_db
from elife_app.data_access.dao import WellnessDAO
from elife_app.domain.models import User, DailyEntry
from elife_app.services.wellness_service import WellnessService


def ask_number(prompt, min_val, max_val):
    while True:
        try:
            value = int(input(prompt))
            if min_val <= value <= max_val:
                return value
        except:
            pass
        print("Invalid input.")


def register(dao):
    print("\n📝 Register")

    username = input("Username: ")
    password = input("Password: ")

    while True:
        gender = input("Gender (male/female): ").lower()

        if gender in ["male", "female"]:
            break

    user = User(
        username=username,
        password=password,
        gender=gender
    )

    dao.register_user(user)

    print("✅ Account created!")


def login(dao):
    print("\n🔐 Login")

    username = input("Username: ")
    password = input("Password: ")

    user = dao.login_user(username, password)

    if user:
        print(f"Welcome {user.username} 💗")
        return user

    print("Invalid login.")
    return None


def add_daily_entry(user, dao, service):
    sleep = ask_number("Sleep (1 bad - 3 good): ", 1, 3)
    stress = ask_number("Stress (1 low - 5 high): ", 1, 5)
    water = ask_number("Water (1 low - 3 good): ", 1, 3)
    exercise = ask_number("Exercise (1 no - 2 yes): ", 1, 2)
    mood = ask_number("Mood (1 bad - 3 good): ", 1, 3)
    steps = ask_number("Steps (1 low - 3 high): ", 1, 3)

    period = None
    pain = None
    flow = None

    if user.gender == "female":
        period = ask_number("Period today? (0 no / 1 yes): ", 0, 1)

        if period == 1:
            pain = ask_number("Pain level (1-5): ", 1, 5)
            flow = input("Flow (light/medium/heavy): ")

    entry = DailyEntry(
        user_id=user.id,
        date=date.today(),
        sleep=sleep,
        stress=stress,
        water=water,
        exercise=exercise,
        mood=mood,
        steps=steps,
        period=period,
        pain=pain,
        flow=flow
    )

    service.calculate_score(entry)
    dao.add_entry(entry)

    print(f"\n✅ Entry saved! Score: {entry.score}")

    advice = service.get_advice(entry)

    if advice:
        print("💡 Advice:")
        for item in advice:
            print(item)


def user_menu(user, dao, service):
    while True:
        print("\n1. Add Daily Entry")
        print("2. Weekly Report")
        print("3. Logout")

        choice = ask_number("Choose: ", 1, 3)

        if choice == 1:
            add_daily_entry(user, dao, service)

        elif choice == 2:
            entries = dao.get_user_entries(user.id)
            print(service.weekly_report(entries))

        elif choice == 3:
            break


def main():
    create_db()

    dao = WellnessDAO()
    service = WellnessService()

    while True:
        print("\n💗 WELLNESS TRACKER 💗")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = ask_number("Choose: ", 1, 3)

        if choice == 1:
            register(dao)

        elif choice == 2:
            user = login(dao)

            if user:
                user_menu(user, dao, service)

        elif choice == 3:
            print("Goodbye ✨")
            break


main()
