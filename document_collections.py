def input_collection(config, console) -> str:        
    console.print("[cyan]Available collections:", ', '.join(config["documents"]["collections"].keys()))
    collection_name = console.input("[cyan]Please select collection: ")

    if not collection_name in config["documents"]["collections"]:
        raise Exception("invalid collection")
    
    return collection_name