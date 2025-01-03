# FaultExplainer

## Video Demo

[![Video Demo](https://img.youtube.com/vi/AIrq0ulJt1E/0.jpg)](https://youtu.be/AIrq0ulJt1E)

This project consists of a backend and a frontend. It requires a valid `OPENAI_API_KEY` to be placed in `backend/.env`

## Backend

To run the backend, follow these steps:

1. Create a virtual environment and install necessary packages `pip install -r backend/requirements.txt`.
2. Change directory to the backend folder: `cd backend`.
3. Run the backend application: `fastapi dev app.py`.

## Frontend

To start the frontend, follow these steps:

1. Start up a new terminal and change directory to the frontend folder: `cd frontend`.
2. Install the required dependencies using yarn: `yarn`.
3. Start the frontend development server: `yarn dev`.

## Citation

If you find this work useful in your research, please consider citing:

```bibtex
@article{khan2024faultexplainer,
  title={FaultExplainer: Leveraging Large Language Models for Interpretable Fault Detection and Diagnosis},
  author={Khan, Abdullah and Nahar, Rahul and Chen, Hao and Flores, Gonzalo E and Li, Can},
  journal={arXiv preprint arXiv:2412.14492},
  year={2024}
}
