
import java.util.*;
import java.text.SimpleDateFormat;

public class WinTime {

    //static final long wintime = 633533725320003750l;
    // 2008-08-04 01:39
    static final long wintime = 633534107180007500l;
    static void log(String msg){
	System.out.println(msg);
    }
    public static void main(String[] args){
	try {

	    log("wintime: "+wintime);
	    long now = new Date().getTime();
	    log("    now: "+now);
	    
	    SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
	    
	    log("    now: "+df.format(new Date()));
	    
	    String nowStr = df.format(new Date());
	    Date pnow = df.parse(nowStr);
	    log("parsed now: "+pnow);

	    String winEpochStr = "1601-01-01 00:00:00";
	    Date winEpoch = df.parse(winEpochStr);
	    log("parsed win epoch: "+winEpoch);
	    log("win epoch.getTime: "+winEpoch.getTime());

	    String tedEpochStr = "01-01-02 23:00:00";
	    Date tedEpoch = df.parse(tedEpochStr);
	    log("parsed ted epoch: "+tedEpoch);
	    log("ted epoch.getTime: "+tedEpoch.getTime());



	    long converted = wintime / 10000l + tedEpoch.getTime();
	    log("    cnv: "+df.format(new Date(converted)));
	    
	} catch (Exception e) {}
    }

}