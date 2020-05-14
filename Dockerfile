FROM python:3.7

# Dockerfile Environment and Defaults
ENV METERID 00000000000000000
ENV MEMBERID 00000
ENV SETTLEMENT_POINT LZ_NORTH
ENV API_URL https://app.gogriddy.com/api/v1/insights/getnow
ENV TDU_CHARGE 3.5
ENV COLLECTION_INTERVAL 60
ENV HTTP_PORT 3000

# Code Elements
WORKDIR /usr/src/app
COPY griddy.py ./
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 3000
CMD ["python" , "./griddy.py", "-v"]
