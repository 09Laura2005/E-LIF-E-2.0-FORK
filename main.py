def main():
    try:
        from elife_app.application import ElifeApplication

        app = ElifeApplication()
        app.run()
    except KeyboardInterrupt:
        print("\nE-LIF-E app stopped.")


if __name__ == "__main__":
    main()
