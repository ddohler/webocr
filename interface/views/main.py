from decorators import login_required

@login_required
def main(request):
    return render_to_response('main.html', {'msg': "Hello, world!"})
    # Display file upload form