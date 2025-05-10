from detect_shapes import ShapeDetector

def main():
    """Main function with error handling"""
    try:
        print("Starting Shape Detector...")
        detector = ShapeDetector()  # Try to run at 60fps
        if detector.start_camera_stream():
            detector.run_detection()
        else:
            print("Failed to start camera stream. Exiting.")
    except KeyboardInterrupt:
        print("Program interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        print("Exiting program")
        if 'detector' in locals():
            detector.cleanup()

if __name__ == "__main__":
    main()