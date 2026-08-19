from fastapi import APIRouter, status, Depends, Request, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from schema.user import (
	UserCreateSchema,
	UserResponseSchema,
	LoginSchema,
	UserLoginResponseSchema,
	ContinueWithGoogleSchema,
	UserUpdateSchema,
	PasswordSchema,
	UpdatePasswordSchema,
	VerifyOTPSchema,
	SupportRequestSchema,
)
from services.models import UserModel
import services.controller as controller
import services.send_email
import services.sign_in_with_google
from services.db import get_db

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserLoginResponseSchema)
def register_endpoint(user: UserCreateSchema, db: Session = Depends(get_db)):
	return controller.register(user, db)


@router.post("/login_with_google", status_code=status.HTTP_200_OK, response_model=UserLoginResponseSchema)
async def login_with_google_endpoint(user: ContinueWithGoogleSchema, db: Session = Depends(get_db)):
	return await services.sign_in_with_google.login_with_google(user, db)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserLoginResponseSchema)
def login_endpoint(user: LoginSchema, db: Session = Depends(get_db)):
	return controller.login(user, db)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_endpoint():
	return controller.logout()


@router.post("/is-authenticated", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
@router.post("/is-authenticat", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
def is_authenticat_endpoint(request: Request, db: Session = Depends(get_db)):
	return controller.is_authenticated(request, db)


@router.post("/forget-password", status_code=status.HTTP_200_OK)
def send_otp_endpoint(
	email: str,
	background_tasks: BackgroundTasks,
	db: Session = Depends(get_db),
):
	user = db.query(UserModel).filter(UserModel.email == email).first()
	if not user:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email not found")

	otp_response = services.send_email.send_otp_email(
		email_to=email,
		background_tasks=background_tasks,
	)

	# Save OTP to database
	controller.save_otp(email, otp_response["otp"], db)

	# Do NOT return OTP to client in production, but for now we'll keep it for debugging or remove it.
	# The user asked to fix the partial bug (sending OTP to client), so I will remove it from response.
	return {"message": "OTP sent successfully", "user_id": user.id}


@router.post("/verify-otp", status_code=status.HTTP_200_OK)
def verify_otp_endpoint(body: VerifyOTPSchema, db: Session = Depends(get_db)):
	return controller.verify_otp(body.email, body.otp, db)


@router.put("/update-password", status_code=status.HTTP_200_OK)
def update_password_endpoint(user_id: int, body: UpdatePasswordSchema, db: Session = Depends(get_db)):
	return controller.update_password(user_id, body.new_password, db)


@router.get("/get_user_info/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
def get_user_endpoint(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
	return controller.get_user(user_id, db)


@router.put("/update_user_info/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
def update_user_info_endpoint(user_id: int, body: UserUpdateSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
	return controller.update_user_info(user_id, body, db)


@router.delete("/remove_user/{user_id}", status_code=status.HTTP_200_OK)
def delete_user_endpoint(user_id: int, body: PasswordSchema, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
	return controller.delete_user(user_id, body.password, db)


@router.post("/verify-password-only", status_code=status.HTTP_200_OK)
def verify_password_only_endpoint(body: PasswordSchema, current_user: UserModel = Depends(controller.is_authenticated)):
	if not controller.verify_password(body.password, current_user.password):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
	return {"message": "Password verified"}


@router.get("/check-subscription", status_code=status.HTTP_200_OK)
def check_subscription_endpoint(user_id: int, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
	return controller.check_subscription(user_id, db)

@router.get("/credits", status_code=status.HTTP_200_OK, response_model=UserResponseSchema)
def get_credits_endpoint(db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
    return controller.get_user_credits(current_user, db)

@router.post("/update-subscription", status_code=status.HTTP_200_OK)
def update_subscription_endpoint(user_id: int, subscription_type: str, subscription_days: int, db: Session = Depends(get_db), current_user: UserModel = Depends(controller.is_authenticated)):
	if current_user.id != user_id:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
	return controller.update_subscription(user_id, subscription_type, subscription_days, db)


@router.post("/submit-support", status_code=status.HTTP_200_OK)
def submit_support_endpoint(
	body: SupportRequestSchema,
	background_tasks: BackgroundTasks,
):
	success = services.send_email.send_support_email(
		email_from=body.email,
		category=body.category,
		details=body.details,
		background_tasks=background_tasks,
	)

	if not success:
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Failed to send support email. Please try again later."
		)

	return {"message": "Support request submitted successfully"}
