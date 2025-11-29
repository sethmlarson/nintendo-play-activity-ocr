FROM docker.io/pytorch/pytorch

# Configure apt and install packages
RUN apt-get update -y && \
    apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-dev \
    git \
    # cleanup
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists

# Clone, build EasyOCR, and load the English language model.
RUN git clone "https://github.com/JaidedAI/EasyOCR.git" --branch v1.7.2 --single-branch \
    && cd "EasyOCR" \
    && python setup.py build_ext --inplace -j 4 \
    && python -m pip install 'numpy<2' -e . \
    && python -c "import easyocr; easyocr.Reader(['en'])"

COPY ocr.py /
ENTRYPOINT ["python", "/ocr.py"]
