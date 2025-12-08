import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.agent import Jarvis

def test_model_switching():
    print("Testing model switching...")
    jarvis = Jarvis()
    
    # Test switching to research mode
    print("\n1. Switching to research mode...")
    jarvis.switch_model("research")
    
    # Test switching to general mode
    print("\n2. Switching to general mode...")
    jarvis.switch_model("general")
    
    # Test switching back to coding mode
    print("\n3. Switching back to coding mode...")
    jarvis.switch_model("coding")
    
    # Test invalid mode
    print("\n4. Testing invalid mode...")
    jarvis.switch_model("invalid")
    
    print("\n✅ Model switching test completed!")

if __name__ == "__main__":
    test_model_switching()
