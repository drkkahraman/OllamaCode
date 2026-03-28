import sys

def my_function(param1, param2):
    return f"Plugin executed with params: {param1}, {param2}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ollamacode run test_plugin.py <param1> <param2>")
        sys.exit(1)
    
    param1 = sys.argv[1]
    param2 = sys.argv[2]
    result = my_function(param1, param2)
    print(result)
