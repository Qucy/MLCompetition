import java.text.DecimalFormat;
import java.text.NumberFormat;

public class Transform {


    static double x_PI = 3.14159265358979324 * 3000.0 / 180.0;
    static double PI = 3.1415926535897932384626;
    static double a = 6378245.0;
    static double ee = 0.00669342162296594323;


    static NumberFormat lat_formatter = new DecimalFormat("#00.00000");
    static NumberFormat lng_formatter = new DecimalFormat("#00.00000");


    /**
     * BD-09 transform to GCJ-02
     * BaiDu coordinate to Google, GaoDe coordinate
     * @param bd_lon BaiDu longitude
     * @param bd_lat BaiDu latitude
     */
    public String  bd09togcj02(double bd_lon, double bd_lat){
        double x = bd_lon - 0.0065;
        double y = bd_lat - 0.006;
        double z = Math.sqrt(x * x + y * y) - 0.00002 * Math.sin(y * x_PI);
        double theta = Math.atan2(y, x) - 0.000003 * Math.cos(x * x_PI);
        double gg_lng = z * Math.cos(theta);
        double gg_lat = z * Math.sin(theta);
        return gg_lng + "," + gg_lat;
    }

    /**
     * GCJ-02 to BD-09
     * Google, GaoDe coordinate to BaiDu coordinate
     * @param lng  GCJ longitude
     * @param lat  GCJ latitude
     */
    public static String gcj02tobd09(double lng, double lat){
        double z = Math.sqrt(lng * lng + lat * lat) + 0.00002 * Math.sin(lat * x_PI);
        double theta = Math.atan2(lat, lng) + 0.000003 * Math.cos(lng * x_PI);
        double bd_lng = z * Math.cos(theta) + 0.0065;
        double bd_lat = z * Math.sin(theta) + 0.006;
        return bd_lng + "," + bd_lat;
    };

    /**
     * WGS84 to GCj02
     * @param lng WGS84 longitude
     * @param lat WGS84 latitude
     */
    public static String wgs84togcj02(double lng, double lat){
        double dlat = transformlat(lng - 105.0, lat - 35.0);
        double dlng = transformlng(lng - 105.0, lat - 35.0);
        double radlat = lat / 180.0 * PI;
        double magic = Math.sin(radlat);
        magic = 1 - ee * magic * magic;
        double sqrtmagic = Math.sqrt(magic);
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI);
        dlng = (dlng * 180.0) / (a / sqrtmagic * Math.cos(radlat) * PI);
        double mglat = lat + dlat;
        double mglng = lng + dlng;
        return mglng + "," + mglat;
    };

    /**
     * GCJ02 transform to WGS84
     * @param lng GCJ02 longitude
     * @param lat GCJ02 latitude
     */
    public String gcj02towgs84(double lng, double lat){
        double dlat = transformlat(lng - 105.0, lat - 35.0);
        double dlng = transformlng(lng - 105.0, lat - 35.0);
        double radlat = lat / 180.0 * PI;
        double magic = Math.sin(radlat);
        magic = 1 - ee * magic * magic;
        double sqrtmagic = Math.sqrt(magic);
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI);
        dlng = (dlng * 180.0) / (a / sqrtmagic * Math.cos(radlat) * PI);
        double mglat = lat + dlat;
        double mglng = lng + dlng;
        return mglat + "," + mglng;
    };

    /**
     * WGS84 to BD-09
     * @param lng WGS84 longitude
     * @param lat WGS84 latitude
     *
     */
    private static String  wgs84tobd09(double lng, double lat){
        // First transform
        double dlat = transformlat(lng - 105.0, lat - 35.0);
        double dlng = transformlng(lng - 105.0, lat - 35.0);
        double radlat = lat / 180.0 * PI;
        double magic = Math.sin(radlat);
        magic = 1 - ee * magic * magic;
        double sqrtmagic = Math.sqrt(magic);
        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * PI);
        dlng = (dlng * 180.0) / (a / sqrtmagic * Math.cos(radlat) * PI);
        double mglat = lat + dlat;
        double mglng = lng + dlng;

        // Second transform
        double z = Math.sqrt(mglng * mglng + mglat * mglat) + 0.00002 * Math.sin(mglat * x_PI);
        double theta = Math.atan2(mglat, mglng) + 0.000003 * Math.cos(mglng * x_PI);
        double bd_lng = z * Math.cos(theta) + 0.0065;
        double bd_lat = z * Math.sin(theta) + 0.006;
        // format before return
        return lng_formatter.format(bd_lng) + "," + lat_formatter.format(bd_lat);
    }

    private static double transformlat(double lng,double lat){
        double ret= -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + 0.1 * lng * lat + 0.2 * Math.sqrt(Math.abs(lng));
        ret += (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0;
        ret += (20.0 * Math.sin(lat * PI) + 40.0 * Math.sin(lat / 3.0 * PI)) * 2.0 / 3.0;
        ret += (160.0 * Math.sin(lat / 12.0 * PI) + 320 * Math.sin(lat * PI / 30.0)) * 2.0 / 3.0;
        return ret;
    }

    private static double transformlng(double lng,double lat){
        double ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + 0.1 * lng * lat + 0.1 * Math.sqrt(Math.abs(lng));
        ret += (20.0 * Math.sin(6.0 * lng * PI) + 20.0 * Math.sin(2.0 * lng * PI)) * 2.0 / 3.0;
        ret += (20.0 * Math.sin(lng * PI) + 40.0 * Math.sin(lng / 3.0 * PI)) * 2.0 / 3.0;
        ret += (150.0 * Math.sin(lng / 12.0 * PI) + 300.0 * Math.sin(lng / 30.0 * PI)) * 2.0 / 3.0;
        return ret;
    }

    // Test
    public static void main(String[] args) {

        double[][] grids = new double[][]{
                {31.195, 31.2, 121.315, 121.32},
                {31.22, 31.225, 121.355, 121.36},
                {31.26, 31.265, 121.485, 121.49},
                {31.15, 31.155, 121.51, 121.515},
                {31.19, 31.195, 121.77, 121.775},
                {31.23, 31.235, 121.37, 121.375},
                {31.22, 31.225, 121.41, 121.415},
                {31.15, 31.155, 121.48, 121.485},
                {31.265, 31.27, 121.485, 121.49},
                {31.205, 31.21, 121.55, 121.555},
                {31.21, 31.215, 121.57, 121.575},
                {31.17, 31.175, 121.34, 121.345},
                {31.19, 31.195, 121.36, 121.365},
                {31.225, 31.23, 121.37, 121.375},
                {31.26, 31.265, 121.39, 121.395},
                {31.185, 31.19, 121.42, 121.425},
                {31.18, 31.185, 121.435, 121.44},
                {31.29, 31.295, 121.435, 121.44},
                {31.245, 31.25, 121.465, 121.47},
                {31.29, 31.295, 121.505, 121.51},
                {31.205, 31.21, 121.515, 121.52},
                {31.29, 31.295, 121.515, 121.52},
                {31.31, 31.315, 121.53, 121.535},
                {31.185, 31.19, 121.355, 121.36},
                {31.195, 31.2, 121.375, 121.38},
                {31.2, 31.205, 121.39, 121.395},
                {31.205, 31.21, 121.4, 121.405},
                {31.235, 31.24, 121.405, 121.41},
                {31.21, 31.215, 121.41, 121.415},
                {31.19, 31.195, 121.415, 121.42},
                {31.195, 31.2, 121.415, 121.42},
                {31.25, 31.255, 121.43, 121.435},
                {31.255, 31.26, 121.43, 121.435},
                {31.26, 31.265, 121.435, 121.44},
                {31.225, 31.23, 121.44, 121.445},
                {31.26, 31.265, 121.44, 121.445},
                {31.23, 31.235, 121.445, 121.45},
                {31.26, 31.265, 121.45, 121.455},
                {31.27, 31.275, 121.45, 121.455},
                {31.235, 31.24, 121.455, 121.46},
                {31.235, 31.24, 121.46, 121.465},
                {31.24, 31.245, 121.46, 121.465},
                {31.245, 31.25, 121.46, 121.465},
                {31.225, 31.23, 121.465, 121.47},
                {31.27, 31.275, 121.465, 121.47},
                {31.235, 31.24, 121.475, 121.48},
                {31.275, 31.28, 121.475, 121.48},
                {31.28, 31.285, 121.475, 121.48},
                {31.235, 31.24, 121.48, 121.485},
                {31.3, 31.305, 121.505, 121.51},
                {31.195,31.2,121.32,121.325},
                {31.18,31.185,121.33,121.335},
                {31.175,31.18,121.335,121.34},
                {31.215,31.22,121.415,121.42},
                {31.185,31.19,121.505,121.51},
                {31.135,31.14,121.395,121.4},
                {31.155,31.16,121.405,121.41},
                {31.21,31.215,121.53,121.535},
                {31.24,31.245,121.56,121.565},
                {31.17,31.175,121.335,121.34},
                {31.175,31.18,121.345,121.35},
                {31.18,31.185,121.345,121.35},
                {31.185,31.19,121.35,121.355},
                {31.235,31.24,121.375,121.38},
                {31.255,31.26,121.385,121.39},
                {31.135,31.14,121.4,121.405},
                {31.215,31.22,121.405,121.41},
                {31.23,31.235,121.405,121.41},
                {31.19,31.195,121.435,121.44},
                {31.295,31.3,121.44,121.445},
                {31.28,31.285,121.445,121.45},
                {31.21,31.215,121.495,121.5},
                {31.235,31.24,121.505,121.51},
                {31.305,31.31,121.51,121.515},
                {31.28,31.285,121.52,121.525},
                {31.28,31.285,121.525,121.53},
                {31.305,31.31,121.525,121.53},
                {31.185,31.19,121.36,121.365},
                {31.19,31.195,121.375,121.38},
                {31.19,31.195,121.385,121.39},
                {31.2,31.205,121.385,121.39},
                {31.205,31.21,121.395,121.4},
                {31.22,31.225,121.405,121.41},
                {31.245,31.25,121.415,121.42},
                {31.25,31.255,121.425,121.43},
                {31.175,31.18,121.43,121.435},
                {31.22,31.225,121.44,121.445},
                {31.23,31.235,121.44,121.445},
                {31.29,31.295,121.445,121.45},
                {31.23,31.235,121.45,121.455},
                {31.28,31.285,121.45,121.455},
                {31.225,31.23,121.46,121.465},
                {31.23,31.235,121.46,121.465},
                {31.265,31.27,121.46,121.465},
                {31.23,31.235,121.465,121.47},
                {31.235,31.24,121.465,121.47},
                {31.2,31.205,121.47,121.475},
                {31.225,31.23,121.47,121.475},
                {31.23,31.235,121.47,121.475},
                {31.27,31.275,121.47,121.475}};

        for(int i=0;i<grids.length;i++) {
            // start point
            double lat_start = grids[i][0];
            double lng_start = grids[i][2];
            String start = wgs84tobd09(lng_start, lat_start);
            
            // end point
            double lat_end = grids[i][1];
            double lng_end = grids[i][3];
            String end = wgs84tobd09(lng_end, lat_end);
            
            System.out.println("[" + (i+1) + "., " + start + "," + end + "],");
        }
    }
}
