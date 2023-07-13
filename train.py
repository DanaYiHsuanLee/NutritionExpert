from ultralytics import YOLO

# Load a pretrained YOLO model (recommended for training)
model = YOLO('yolov8n.pt')

# Train the model using the 'school_lunch.yaml' dataset for 30 epochs
results = model.train(data='food256.yaml', epochs=1)