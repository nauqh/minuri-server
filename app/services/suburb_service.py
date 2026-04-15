def get_suburb_service():
    """
    Possible suburbs 2026:
    Carlton
    City of Melbourne
    Docklands
    East Melbourne
    Kensington
    Melbourne (CBD)
    Melbourne (Remainder)
    North Melbourne
    Parkville
    Port Melbourne
    South Yarra
    Southbank
    West Melbourne (Industrial)
    West Melbourne (Residential)
    """
    try:
        suburbs = [
            "Carlton",
            "City of Melbourne",
            "Docklands",
            "East Melbourne",
            "Kensington",
            "Melbourne (CBD)",
            "Melbourne (Remainder)",
            "North Melbourne",
            "Parkville",
            "Port Melbourne",
            "South Yarra",
            "Southbank",
            "West Melbourne (Industrial)",
            "West Melbourne (Residential)",
        ]
        return {"suburbs": suburbs}
    except Exception as e:
        return {"error": str(e)}
