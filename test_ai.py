"""
Test script for AI Advisor functionality
"""
from ai_advisor import AIAdvisor
import config

def test_ai_advisor():
    """Test AI Advisor with sample trading data"""
    
    print("=" * 60)
    print("Testing AI Advisor")
    print("=" * 60)
    
    try:
        # Create AI Advisor instance
        print(f"\n1. Initializing AI Advisor at {config.AI_API_URL}...")
        ai = AIAdvisor(config.AI_API_URL)
        
        # Check if AI is enabled
        if not ai.is_enabled():
            print("❌ AI service is not available!")
            print("   Make sure your AI service is running")
            print(f"   Expected URL: {config.AI_API_URL}")
            return
        
        print("✅ AI service is online and ready!")
        status = ai.get_status()
        print(f"   Status: {status}")
        
        # Test 1: analyze_trade_opportunity
        print("\n" + "=" * 60)
        print("2. Testing analyze_trade_opportunity (BUY signal)")
        print("=" * 60)
        
        test_stats = {
            'total_trades': 5,
            'wins': 3,
            'losses': 2,
            'win_rate': 60.0
        }
        
        signal = 'BUY'
        price = 43000.00
        
        print(f"\nSignal: {signal}")
        print(f"Price: ${price:,.2f}")
        print(f"Stats: {test_stats}")
        print("\nAsking AI for trade analysis...")
        
        response = ai.analyze_trade_opportunity(signal, price, test_stats)
        
        if response:
            print("\n🤖 AI Response:")
            print("-" * 60)
            print(response)
            print("-" * 60)
        else:
            print("❌ No response received from AI")
        
        # Test 2: send_daily_summary
        print("\n" + "=" * 60)
        print("3. Testing send_daily_summary")
        print("=" * 60)
        
        test_balance = {
            'USDT': 1500.75,
            'BTC': 0.03456789
        }
        
        print(f"\nStats: {test_stats}")
        print(f"Balance: {test_balance}")
        print("\nSending daily summary to AI...")
        
        feedback = ai.send_daily_summary(test_stats, test_balance)
        
        if feedback:
            print("\n🤖 AI Feedback:")
            print("-" * 60)
            print(feedback)
            print("-" * 60)
        else:
            print("❌ No feedback received from AI")
        
        # Test 3: ask_for_suggestions
        print("\n" + "=" * 60)
        print("4. Testing ask_for_suggestions")
        print("=" * 60)
        
        buy_threshold = 1.0
        sell_threshold = 1.0
        
        print(f"\nBuy Threshold: {buy_threshold}%")
        print(f"Sell Threshold: {sell_threshold}%")
        print(f"Stats: {test_stats}")
        print("\nAsking AI for optimization suggestions...")
        
        suggestions = ai.ask_for_suggestions(buy_threshold, sell_threshold, test_stats)
        
        if suggestions:
            print("\n🤖 AI Suggestions:")
            print("-" * 60)
            print(suggestions)
            print("-" * 60)
        else:
            print("❌ No suggestions received from AI")
        
        # Test 4: HOLD signal (should return None)
        print("\n" + "=" * 60)
        print("5. Testing HOLD signal (should skip AI)")
        print("=" * 60)
        
        hold_response = ai.analyze_trade_opportunity('HOLD', price, test_stats)
        
        if hold_response is None:
            print("✅ HOLD signal correctly returns None (no AI consultation)")
        else:
            print(f"⚠️ Unexpected response for HOLD: {hold_response}")
        
        print("\n" + "=" * 60)
        print("✅ All AI Advisor tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ai_advisor()
