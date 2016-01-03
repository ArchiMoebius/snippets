public class GestureManager extends GestureDetector.SimpleOnGestureListener
{
    public static final int SWIPE_MIN_DISTANCE = 120;
    public static final int SWIPE_MAX_OFF_PATH = 250;
    public static final int SWIPE_THRESHOLD_VELOCITY = 200;
    public Intent LeftIntent = null;
    public Intent RightIntent = null;
    public Context ctx = null;
    public Activity parent = null;
    public Class<?> LeftClass = null;
    public Class<?> RightClass = null;

    /*
    * after setting the ctx, parent and respective Xclass (Left/Right) you will be able todo gesture based navigation.
    */
    public boolean onFling(MotionEvent e1, MotionEvent e2, float velocityX, float velocityY)
    {

        if (Math.abs(e1.getY() - e2.getY()) > SWIPE_MAX_OFF_PATH)
        {
            return false;
        }

        if(ctx == null || parent == null)
        	return false;

        // left to right swipe
        if(e1.getX() - e2.getX() > SWIPE_MIN_DISTANCE && Math.abs(velocityX) > SWIPE_THRESHOLD_VELOCITY)
        {
        	if(RightClass == null)
        		return false;

            if (RightIntent == null)
            {
            	RightIntent = new Intent();
            	RightIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            	RightIntent.setClass(ctx, RightClass);
            }

            ctx.startActivity(RightIntent);
	
            parent.overridePendingTransition(
            	R.anim.center_scale_to_full,
				R.anim.slide_out_left
			);
            parent.finish();
            RightClass = null;
	    // right to left swipe
        }
        else if (e2.getX() - e1.getX() > SWIPE_MIN_DISTANCE && Math.abs(velocityX) > SWIPE_THRESHOLD_VELOCITY)
        {
        	if(LeftClass == null)
        		return false;

            if (LeftIntent == null)
            {
            	LeftIntent = new Intent();
            	LeftIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            	LeftIntent.setClass(ctx, LeftClass);
            }

            ctx.startActivity(LeftIntent);

            parent.overridePendingTransition(
                R.anim.center_scale_to_full, 
				R.anim.slide_out_right
			);
            parent.finish();
            LeftClass = null;
        }

        return false;
    }

    // It is necessary to return true from onDown for the onFling event to register
    @Override
    public boolean onDown(MotionEvent e)
    {
        	return true;
    }
}

