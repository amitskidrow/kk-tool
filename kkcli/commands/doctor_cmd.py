def register(subparsers):
    p = subparsers.add_parser("doctor", help="Diagnose keyring/DBus and show context")
    p.set_defaults(func=run)


def run(args):
    # Try imports and open default store in both modes to report status
    report = []
    try:
        import secretstorage  # noqa
        report.append("secretstorage: OK")
    except Exception as e:
        report.append(f"secretstorage: ERROR: {e}")
        print("\n".join(report))
        return
    try:
        bus = secretstorage.dbus_init()
        report.append("DBus: OK")
        coll = secretstorage.get_default_collection(bus)
        label = coll.get_label()
        locked = coll.is_locked()
        report.append(f"Default collection: '{label}', locked={locked}")
    except Exception as e:
        report.append(f"DBus/Collection: ERROR: {e}")
    print("\n".join(report))

