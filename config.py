import cloudinary
import cloudinary.uploader
import cloudinary.api

# Configure Cloudinary
cloudinary.config(
    cloud_name = "dm8vkxuws",
    api_key = "536282497719588",
    api_secret = "LKJtWYQRqF6GDcexczyZlZJxQAM"
)

# Add a test function to verify configuration
def test_cloudinary_config():
    try:
        # Test the configuration by trying to upload a test image
        test_response = cloudinary.uploader.upload(
            "https://res.cloudinary.com/demo/image/upload/sample.jpg",
            public_id="test_connection",
            overwrite=True
        )
        print("Cloudinary configuration is valid!")
        print(f"Test upload successful: {test_response['secure_url']}")
        
        # Clean up test image
        cloudinary.uploader.destroy("test_connection")
        return True
    except Exception as e:
        print(f"Cloudinary configuration error: {str(e)}")
        return False

if __name__ == "__main__":
    test_cloudinary_config()
