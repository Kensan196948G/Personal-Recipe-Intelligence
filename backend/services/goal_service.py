"""
Goal Service - Alias for HealthGoalService

This module provides backward compatibility by aliasing HealthGoalService as GoalService.
"""

from backend.services.health_goal_service import HealthGoalService

# Alias for backward compatibility
GoalService = HealthGoalService

__all__ = ["GoalService"]
