"""
Backwards compatibility module - imports from refactored user and project controllers
"""
from services.user_controller import (
    get_password_hash,
    verify_password,
    create_access_token,
    is_authenticated,
    register,
    login,
    update_password,
    save_otp,
    verify_otp,
    update_user_info,
    get_user,
    check_subscription,
    update_subscription,
    logout,
    continue_with_google,
    delete_user,
    is_authenticat,
    get_user_credits,
    handle_credits_reset,
    consume_credits,
)

from services.project_controller import (
    create_project,
    get_projects,
    delete_project,
    update_project,
    get_project_visibility,
    update_project_visibility,
    get_public_projects,
    update_project_image_url,
)

__all__ = [
    # User functions
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "is_authenticated",
    "register",
    "login",
    "update_password",
    "save_otp",
    "verify_otp",
    "update_user_info",
    "get_user",
    "check_subscription",
    "update_subscription",
    "logout",
    "continue_with_google",
    "delete_user",
    "is_authenticat",
    "get_user_credits",
    "handle_credits_reset",
    "consume_credits",
    # Project functions
    "create_project",
    "get_projects",
    "delete_project",
    "update_project",
    "get_project_visibility",
    "update_project_visibility",
    "get_public_projects",
    "update_project_image_url",
]



    