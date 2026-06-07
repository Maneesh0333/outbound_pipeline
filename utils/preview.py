def preview(leads):
    """Print a formatted table of leads that will be contacted."""
    if not leads:
        print("No leads to preview.")
        return

    col_name    = max(len(p.get("full_name") or "") for p in leads)
    col_title   = max(len(p.get("title") or "")     for p in leads)
    col_email   = max(len(p.get("email") or "")     for p in leads)

    col_name  = max(col_name,  8)
    col_title = max(col_title, 5)
    col_email = max(col_email, 5)

    header = (
        f"  {'Name':<{col_name}}  "
        f"{'Title':<{col_title}}  "
        f"{'Email':<{col_email}}"
    )
    divider = "  " + "-" * (col_name + col_title + col_email + 6)

    print(f"\n{'─' * len(header)}")
    print(f"  {len(leads)} lead(s) ready to contact")
    print(f"{'─' * len(header)}")
    print(header)
    print(divider)

    for p in leads:
        name  = (p.get("full_name") or "")[:col_name]
        title = (p.get("title")     or "")[:col_title]
        email = (p.get("email")     or "")
        print(
            f"  {name:<{col_name}}  "
            f"{title:<{col_title}}  "
            f"{email:<{col_email}}"
        )

    print(f"{'─' * len(header)}\n")
