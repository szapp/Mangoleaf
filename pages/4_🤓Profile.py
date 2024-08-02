"""
User profile
"""

import os

import streamlit as st
from PIL import Image

from mangoleaf import authentication, frontend

frontend.add_config()
frontend.add_style()
frontend.add_sidebar_login()
frontend.add_sidebar_logo()

frontend.add_header_logo("User Profile")

# Check if the user is authenticated
if not authentication.is_authenticated():
    st.warning("Please log in from the home page to access this page.")
    st.stop()  # Stop further execution if not authenticated

user_data = authentication.get_user_info()

st.markdown(f"**Username:** {user_data['username']}")
st.markdown(f"**Name:** {user_data['full_name']}")

# Profile picture upload

# Directory to store uploaded images
UPLOAD_FOLDER = "uploaded_images"

# Ensure the directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def save_image(image_file, user_id):
    """Save the uploaded image to a file."""
    file_path = os.path.join(UPLOAD_FOLDER, f"{user_id}.png")
    with open(file_path, "wb") as f:
        f.write(image_file.getbuffer())
    return file_path


def load_image(user_id):
    """Load the saved image for the user."""
    file_path = os.path.join(UPLOAD_FOLDER, f"{user_id}.png")
    if os.path.exists(file_path):
        return Image.open(file_path)
    return None


def user_profile(user_id):
    """Display the user profile page."""

    # Load and display the existing profile image
    profile_image = load_image(user_id)

    if profile_image is not None:
        st.image(profile_image, caption="Profile Picture", width=150)

        # Show update button if an image is already uploaded
        if st.button("Update Profile Picture"):
            image_file = st.file_uploader(
                "Upload a new profile picture", type=["png", "jpg", "jpeg"]
            )

            if image_file is not None:
                if image_file.size > 2 * 1024 * 1024:  # 2MB limit
                    st.error("File size exceeds the 2MB limit. Please upload a smaller file.")
                else:
                    # Save the uploaded image
                    save_image(image_file, user_id)
                    st.success("Profile picture updated!")
                    st.image(load_image(user_id), caption="Profile Picture", width=150)
    else:
        # Show upload option if no image is uploaded yet
        image_file = st.file_uploader("Upload your profile picture", type=["png", "jpg", "jpeg"])

        if image_file is not None:
            if image_file.size > 2 * 1024 * 1024:  # 2MB limit
                st.error("File size exceeds the 2MB limit. Please upload a smaller file.")
            else:
                # Save the uploaded image
                save_image(image_file, user_id)
                st.success("Profile picture uploaded!")
                st.image(load_image(user_id), caption="Profile Picture", width=150)


user_profile(user_data["user_id"])

if st.button("Logout"):
    authentication.reset()
    st.success("You have logged out.")
    st.rerun()
