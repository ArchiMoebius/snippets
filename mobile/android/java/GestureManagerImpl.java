final GestureManager gm = new GestureManager();

gm.LeftClass = ConfigurationActivity.class;
gm.ctx = getBaseContext(); 
gm.parent = this;

final GestureDetector gestureDetector = new GestureDetector(gm);
View mainview = (View) findViewById(R.id.mainView);

mainview.setOnTouchListener(new View.OnTouchListener()
{
	public boolean onTouch(View v, MotionEvent event)
        {
        	if (gestureDetector.onTouchEvent(event))
                {
                    return true;
                }
                return false;
            }
});
