from helpers import render_template

def index(request):
    return render_template('index.html', request)
    
def tutorial(request):
    return render_template('tutorial.html', request)
    
def about(request):
    return render_template('about.html', request)