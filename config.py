"""
Configuration settings for the Oppenheimer Time Machine.
Adjust these settings to balance cost and quality.
"""
from typing import Dict, List, Tuple

# TTS Cost Management
TTS_CONFIG = {
    # Google Cloud TTS pricing (approximate, as of 2024)
    "cost_per_character": 0.000016,  # $16 per 1M characters
    
    # Daily budget limits
    "max_daily_characters": 50000,   # Adjust based on your budget
    "max_daily_cost": 0.80,         # $0.80 per day limit
    
    # Response length limits by type
    "response_length_limits": {
        "simple_fact": {"min": 50, "max": 200},         # Very short factual answers
        "philosophical": {"min": 300, "max": 600},      # Thoughtful but concise
        "historical": {"min": 400, "max": 800},         # Rich detail when needed
        "personal": {"min": 200, "max": 500},           # Emotional but measured
        "scientific": {"min": 300, "max": 700},         # Clear explanations
        "greeting": {"min": 100, "max": 250}            # Brief introductions
    },
    
    # TTS quality vs cost settings
    "voice_settings": {
        "speaking_rate": 0.9,        # Slightly slower for gravitas
        "pitch": -2.0,               # Lower pitch for authority
        "volume_gain": 0.0,          # Standard volume
        "sample_rate": 24000,        # High quality (vs 16000 for lower cost)
    },
    
    # When to skip TTS entirely
    "skip_tts_if": {
        "response_too_long": 1200,   # Skip if response > 1200 characters
        "budget_depleted": 0.9,      # Skip if 90% of daily budget used
        "error_response": True,      # Skip TTS for error messages
    }
}

# Response Quality Settings
RESPONSE_CONFIG = {
    # How to handle different query types
    "detail_levels": {
        "factual_query": "concise",           # Just the facts
        "exploratory_query": "balanced",      # Some depth but manageable
        "philosophical_query": "detailed",    # Full depth appropriate
        "personal_query": "thoughtful",       # Emotional nuance
        "complex_query": "comprehensive"      # Maximum detail when warranted
    },
    
    # Context management
    "max_conversation_history": 5,    # Keep last 5 exchanges
    "context_window_chars": 4000,     # Max context length
    
    # Response optimization
    "enable_smart_truncation": True,   # Intelligently shorten responses
    "preserve_quotes": True,           # Always keep literary quotes intact
    "maintain_persona": True,          # Never compromise character voice
}

# Budget Alert Thresholds
BUDGET_ALERTS = {
    "warning_threshold": 0.7,    # Warn at 70% budget usage
    "critical_threshold": 0.9,   # Critical alert at 90%
    "emergency_threshold": 0.95  # Emergency stop at 95%
}

# User Experience Settings
UX_CONFIG = {
    # When to provide cost feedback to users
    "show_cost_info": True,           # Display cost information
    "notify_tts_skip": True,          # Tell user when TTS is skipped
    "show_response_type": False,      # Show detected response type
    "display_character_count": False, # Show response length
    
    # Response timing
    "typing_simulation": False,       # Simulate typing for realism
    "response_delay": 0.5,           # Minimum delay before response (seconds)
    
    # Audio settings
    "auto_play_audio": True,         # Automatically play audio responses
    "show_audio_controls": True,     # Show play/pause controls
    "volume_default": 0.8,           # Default audio volume
}

# Advanced Cost Optimization
OPTIMIZATION_CONFIG = {
    # Dynamic pricing based on time of day (if applicable)
    "peak_hours": [9, 10, 11, 14, 15, 16],  # Hours with potential higher costs
    "peak_hour_multiplier": 1.2,            # Cost multiplier during peak
    
    # Response caching
    "enable_response_cache": True,           # Cache similar responses
    "cache_similarity_threshold": 0.85,     # How similar to use cached response
    "max_cache_size": 100,                  # Maximum cached responses
    
    # Batch processing
    "enable_batching": False,               # Batch multiple requests (if available)
    "batch_size": 5,                       # Number of requests per batch
    "batch_timeout": 30,                   # Seconds to wait for batch completion
}

# Monitoring and Analytics
MONITORING_CONFIG = {
    "track_usage": True,            # Track detailed usage statistics
    "log_costs": True,              # Log all cost-related events
    "save_analytics": True,         # Save analytics to file
    "analytics_file": "usage_analytics.json",
    
    # Performance metrics
    "track_response_times": True,   # Monitor response generation time
    "track_tts_times": True,       # Monitor TTS synthesis time
    "track_user_satisfaction": False, # Ask for feedback (optional)
}

def get_cost_per_response_estimate(response_length: int) -> float:
    """Get estimated cost for a response of given length."""
    return response_length * TTS_CONFIG["cost_per_character"]

def should_use_premium_voice(daily_usage: int) -> bool:
    """Determine if premium voice settings should be used based on usage."""
    usage_ratio = daily_usage / TTS_CONFIG["max_daily_characters"]
    return usage_ratio < 0.5  # Use premium voice only if under 50% of daily budget

def get_response_length_target(query_type: str, conversation_length: int) -> Tuple[int, int]:
    """Get target response length based on query type and conversation context."""
    base_limits = TTS_CONFIG["response_length_limits"].get(
        query_type, 
        {"min": 200, "max": 500}
    )
    
    # Adjust based on conversation length (shorter responses later in conversation)
    if conversation_length > 10:
        adjustment = 0.8
    elif conversation_length > 5:
        adjustment = 0.9
    else:
        adjustment = 1.0
    
    return (
        int(base_limits["min"] * adjustment),
        int(base_limits["max"] * adjustment)
    )

# Example usage patterns for different scenarios
USAGE_SCENARIOS = {
    "demonstration": {
        "max_daily_characters": 10000,
        "response_length_multiplier": 0.7,
        "description": "Short demo with cost control"
    },
    "educational": {
        "max_daily_characters": 30000,
        "response_length_multiplier": 1.0,
        "description": "Balanced education use"
    },
    "research": {
        "max_daily_characters": 80000,
        "response_length_multiplier": 1.3,
        "description": "Detailed research conversations"
    },
    "production": {
        "max_daily_characters": 20000,
        "response_length_multiplier": 0.8,
        "description": "Cost-optimized production use"
    }
}

def apply_scenario(scenario_name: str) -> None:
    """Apply a predefined usage scenario."""
    if scenario_name in USAGE_SCENARIOS:
        scenario = USAGE_SCENARIOS[scenario_name]
        TTS_CONFIG["max_daily_characters"] = scenario["max_daily_characters"]
        
        # Adjust all response length limits
        multiplier = scenario["response_length_multiplier"]
        for response_type in TTS_CONFIG["response_length_limits"]:
            limits = TTS_CONFIG["response_length_limits"][response_type]
            limits["min"] = int(limits["min"] * multiplier)
            limits["max"] = int(limits["max"] * multiplier)
        
        import logging
        logging.info(f"Applied scenario: {scenario['description']}")
    else:
        import logging
        logging.warning(f"Unknown scenario: {scenario_name}")
        logging.info(f"Available scenarios: {list(USAGE_SCENARIOS.keys())}")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Example: Apply demonstration scenario for cost-controlled demo
    apply_scenario("demonstration")
    
    # Show current configuration
    logging.info("Current TTS Configuration:")
    logging.info(f"Max daily characters: {TTS_CONFIG['max_daily_characters']:,}")
    logging.info(f"Cost per character: ${TTS_CONFIG['cost_per_character']:.6f}")
    logging.info(f"Max daily cost: ${TTS_CONFIG['max_daily_cost']:.2f}")
    
    logging.info("Response Length Limits:")
    for response_type, limits in TTS_CONFIG['response_length_limits'].items():
        logging.info(f"  {response_type}: {limits['min']}-{limits['max']} chars")