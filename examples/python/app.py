from skillbridge import Bridge

bridge = Bridge("PythonDemo")
bridge.expose("greet", "Greet someone", lambda name: f"Hello, {name}!", {"name": "string"})
bridge.expose("add", "Add two integers", lambda a, b: a + b, {"a": "integer", "b": "integer"})
bridge.serve()  # Prints local URL and generated bearer token
