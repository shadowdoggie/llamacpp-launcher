try:
    from ui.main_window import MainWindow
    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
except NameError as e:
    print(f"NameError: {e}")
except Exception as e:
    print(f"Error: {e}")
