# Minimal Makefile with start/stop 
UserAPP = User_Service.app.UserMain:app 
GameAPP = Game_Service.app.GameMain:app
PID_FILE = .uvicorn.pid 
install: 
	pip install -r requirements.txt 
runUsers: 
	python -m uvicorn $(UserAPP) --host 0.0.0.0 --port 8000 --reload 
runGame:
	python -m uvicorn $(GameAPP) --host 0.0.0.0 --port 8001 --reload 
test: 
	python -m pytest -vv -x -l --full-trace