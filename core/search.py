def search_files(query, index):
    results = []
    query = query.lower()

    for entry in index:
        if query in entry["name"].lower() or query in entry["path"].lower():
            results.append(entry)

    return results
