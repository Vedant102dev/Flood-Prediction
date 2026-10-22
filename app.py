from flask import Flask, render_template, request, jsonify
from model.utils import get_city_weather, predict_flood
import concurrent.futures
import requests as req_lib

app = Flask(__name__)

CITIES = [
    {"name": "Mumbai", "state": "Maharashtra", "lat": 19.076, "lon": 72.8777},
    {"name": "Pune", "state": "Maharashtra", "lat": 18.5204, "lon": 73.8567},
    {"name": "Nagpur", "state": "Maharashtra", "lat": 21.1458, "lon": 79.0882},
    {"name": "Thane", "state": "Maharashtra", "lat": 19.2183, "lon": 72.9781},
    {"name": "Nashik", "state": "Maharashtra", "lat": 19.9975, "lon": 73.7898},
    {"name": "Kalyan-Dombivli", "state": "Maharashtra", "lat": 19.2403, "lon": 73.1305},
    {"name": "Vasai-Virar", "state": "Maharashtra", "lat": 19.3919, "lon": 72.8397},
    {"name": "Aurangabad", "state": "Maharashtra", "lat": 19.8762, "lon": 75.3433},
    {"name": "Navi Mumbai", "state": "Maharashtra", "lat": 19.033, "lon": 73.0297},
    {"name": "Solapur", "state": "Maharashtra", "lat": 17.6599, "lon": 75.9064},
    {"name": "Mira-Bhayandar", "state": "Maharashtra", "lat": 19.2812, "lon": 72.8561},
    {"name": "Kolhapur", "state": "Maharashtra", "lat": 16.705, "lon": 74.2433},
    {"name": "Amravati", "state": "Maharashtra", "lat": 20.932, "lon": 77.7523},
    {"name": "Nanded", "state": "Maharashtra", "lat": 19.1383, "lon": 77.321},
    {"name": "Sangli", "state": "Maharashtra", "lat": 16.8524, "lon": 74.5815},
    {"name": "Malegaon", "state": "Maharashtra", "lat": 20.5579, "lon": 74.5287},
    {"name": "Akola", "state": "Maharashtra", "lat": 20.7002, "lon": 77.0082},
    {"name": "Latur", "state": "Maharashtra", "lat": 18.4088, "lon": 76.5604},
    {"name": "Dhule", "state": "Maharashtra", "lat": 20.9042, "lon": 74.7749},
    {"name": "Ahmednagar", "state": "Maharashtra", "lat": 19.0952, "lon": 74.7496},
    {"name": "Chandrapur", "state": "Maharashtra", "lat": 19.9615, "lon": 79.2961},
    {"name": "Parbhani", "state": "Maharashtra", "lat": 19.2686, "lon": 76.771},
    {"name": "Jalgaon", "state": "Maharashtra", "lat": 21.0077, "lon": 75.5626},
    {"name": "Chiplun", "state": "Maharashtra", "lat": 17.5323, "lon": 73.5186},
    {"name": "Mahad", "state": "Maharashtra", "lat": 18.0831, "lon": 73.419},
    {"name": "Ratnagiri", "state": "Maharashtra", "lat": 16.9902, "lon": 73.312},
    {"name": "Alibag", "state": "Maharashtra", "lat": 18.6414, "lon": 72.8722},
    {"name": "Delhi", "state": "Delhi", "lat": 28.6139, "lon": 77.209},
    {"name": "New Delhi", "state": "Delhi", "lat": 28.6143, "lon": 77.1994},
    {"name": "Noida", "state": "Uttar Pradesh", "lat": 28.5355, "lon": 77.391},
    {"name": "Greater Noida", "state": "Uttar Pradesh", "lat": 28.4744, "lon": 77.504},
    {"name": "Ghaziabad", "state": "Uttar Pradesh", "lat": 28.6692, "lon": 77.4538},
    {"name": "Gurugram", "state": "Haryana", "lat": 28.4595, "lon": 77.0266},
    {"name": "Faridabad", "state": "Haryana", "lat": 28.4089, "lon": 77.3178},
    {"name": "Lucknow", "state": "Uttar Pradesh", "lat": 26.8467, "lon": 80.9462},
    {"name": "Kanpur", "state": "Uttar Pradesh", "lat": 26.4499, "lon": 80.3319},
    {"name": "Varanasi", "state": "Uttar Pradesh", "lat": 25.3176, "lon": 82.9739},
    {"name": "Agra", "state": "Uttar Pradesh", "lat": 27.1767, "lon": 78.0081},
    {"name": "Prayagraj", "state": "Uttar Pradesh", "lat": 25.4358, "lon": 81.8463},
    {"name": "Meerut", "state": "Uttar Pradesh", "lat": 28.9845, "lon": 77.7064},
    {"name": "Bareilly", "state": "Uttar Pradesh", "lat": 28.367, "lon": 79.4304},
    {"name": "Aligarh", "state": "Uttar Pradesh", "lat": 27.8974, "lon": 78.088},
    {"name": "Moradabad", "state": "Uttar Pradesh", "lat": 28.8351, "lon": 78.7744},
    {"name": "Saharanpur", "state": "Uttar Pradesh", "lat": 29.9678, "lon": 77.551},
    {"name": "Gorakhpur", "state": "Uttar Pradesh", "lat": 26.7606, "lon": 83.3732},
    {"name": "Firozabad", "state": "Uttar Pradesh", "lat": 27.1594, "lon": 78.3957},
    {"name": "Jhansi", "state": "Uttar Pradesh", "lat": 25.4484, "lon": 78.5685},
    {"name": "Muzaffarnagar", "state": "Uttar Pradesh", "lat": 29.4727, "lon": 77.7085},
    {"name": "Mathura", "state": "Uttar Pradesh", "lat": 27.4924, "lon": 77.6737},
    {"name": "Ayodhya", "state": "Uttar Pradesh", "lat": 26.7922, "lon": 82.1998},
    {"name": "Patna", "state": "Bihar", "lat": 25.5941, "lon": 85.1376},
    {"name": "Gaya", "state": "Bihar", "lat": 24.7914, "lon": 85.0002},
    {"name": "Bhagalpur", "state": "Bihar", "lat": 25.2425, "lon": 86.9842},
    {"name": "Muzaffarpur", "state": "Bihar", "lat": 26.1209, "lon": 85.3647},
    {"name": "Purnia", "state": "Bihar", "lat": 25.7771, "lon": 87.4753},
    {"name": "Darbhanga", "state": "Bihar", "lat": 26.1542, "lon": 85.8918},
    {"name": "Bihar Sharif", "state": "Bihar", "lat": 25.1982, "lon": 85.5149},
    {"name": "Arrah", "state": "Bihar", "lat": 25.556, "lon": 84.6603},
    {"name": "Begusarai", "state": "Bihar", "lat": 25.4182, "lon": 86.1272},
    {"name": "Katihar", "state": "Bihar", "lat": 25.5541, "lon": 87.5722},
    {"name": "Munger", "state": "Bihar", "lat": 25.3757, "lon": 86.4744},
    {"name": "Chhapra", "state": "Bihar", "lat": 25.7848, "lon": 84.7274},
    {"name": "Saharsa", "state": "Bihar", "lat": 25.8835, "lon": 86.6006},
    {"name": "Kolkata", "state": "West Bengal", "lat": 22.5726, "lon": 88.3639},
    {"name": "Howrah", "state": "West Bengal", "lat": 22.5958, "lon": 88.2636},
    {"name": "Siliguri", "state": "West Bengal", "lat": 26.7271, "lon": 88.4236},
    {"name": "Asansol", "state": "West Bengal", "lat": 23.6739, "lon": 86.9524},
    {"name": "Durgapur", "state": "West Bengal", "lat": 23.5204, "lon": 87.3119},
    {"name": "Bardhaman", "state": "West Bengal", "lat": 23.2324, "lon": 87.8615},
    {"name": "Malda", "state": "West Bengal", "lat": 25.0108, "lon": 88.1411},
    {"name": "Baharampur", "state": "West Bengal", "lat": 24.0988, "lon": 88.2685},
    {"name": "Kharagpur", "state": "West Bengal", "lat": 22.346, "lon": 87.232},
    {"name": "Darjeeling", "state": "West Bengal", "lat": 27.041, "lon": 88.2663},
    {"name": "Jalpaiguri", "state": "West Bengal", "lat": 26.5405, "lon": 88.7194},
    {"name": "Cooch Behar", "state": "West Bengal", "lat": 26.3452, "lon": 89.4482},
    {"name": "Bengaluru", "state": "Karnataka", "lat": 12.9716, "lon": 77.5946},
    {"name": "Mysuru", "state": "Karnataka", "lat": 12.2958, "lon": 76.6394},
    {"name": "Hubballi-Dharwad", "state": "Karnataka", "lat": 15.3647, "lon": 75.124},
    {"name": "Mangaluru", "state": "Karnataka", "lat": 12.9141, "lon": 74.856},
    {"name": "Belagavi", "state": "Karnataka", "lat": 15.8497, "lon": 74.4977},
    {"name": "Kalaburagi", "state": "Karnataka", "lat": 17.3297, "lon": 76.8343},
    {"name": "Davanagere", "state": "Karnataka", "lat": 14.4644, "lon": 75.9218},
    {"name": "Ballari", "state": "Karnataka", "lat": 15.1394, "lon": 76.9214},
    {"name": "Vijayapura", "state": "Karnataka", "lat": 16.8302, "lon": 75.71},
    {"name": "Shivamogga", "state": "Karnataka", "lat": 13.9299, "lon": 75.5681},
    {"name": "Tumakuru", "state": "Karnataka", "lat": 13.3379, "lon": 77.101},
    {"name": "Udupi", "state": "Karnataka", "lat": 13.3409, "lon": 74.7421},
    {"name": "Karwar", "state": "Karnataka", "lat": 14.8185, "lon": 74.1303},
    {"name": "Madikeri", "state": "Karnataka", "lat": 12.4244, "lon": 75.7382},
    {"name": "Chennai", "state": "Tamil Nadu", "lat": 13.0827, "lon": 80.2707},
    {"name": "Coimbatore", "state": "Tamil Nadu", "lat": 11.0168, "lon": 76.9558},
    {"name": "Madurai", "state": "Tamil Nadu", "lat": 9.9252, "lon": 78.1198},
    {"name": "Tiruchirappalli", "state": "Tamil Nadu", "lat": 10.7905, "lon": 78.7047},
    {"name": "Salem", "state": "Tamil Nadu", "lat": 11.6643, "lon": 78.146},
    {"name": "Tirunelveli", "state": "Tamil Nadu", "lat": 8.7139, "lon": 77.7567},
    {"name": "Tiruppur", "state": "Tamil Nadu", "lat": 11.1085, "lon": 77.3411},
    {"name": "Vellore", "state": "Tamil Nadu", "lat": 12.9165, "lon": 79.1325},
    {"name": "Erode", "state": "Tamil Nadu", "lat": 11.341, "lon": 77.7172},
    {"name": "Thoothukudi", "state": "Tamil Nadu", "lat": 8.7642, "lon": 78.1348},
    {"name": "Dindigul", "state": "Tamil Nadu", "lat": 10.3673, "lon": 77.9803},
    {"name": "Thanjavur", "state": "Tamil Nadu", "lat": 10.787, "lon": 79.1378},
    {"name": "Cuddalore", "state": "Tamil Nadu", "lat": 11.748, "lon": 79.7714},
    {"name": "Kanyakumari", "state": "Tamil Nadu", "lat": 8.0883, "lon": 77.5385},
    {"name": "Ahmedabad", "state": "Gujarat", "lat": 23.0225, "lon": 72.5714},
    {"name": "Surat", "state": "Gujarat", "lat": 21.1702, "lon": 72.8311},
    {"name": "Vadodara", "state": "Gujarat", "lat": 22.3072, "lon": 73.1812},
    {"name": "Rajkot", "state": "Gujarat", "lat": 22.3039, "lon": 70.8022},
    {"name": "Bhavnagar", "state": "Gujarat", "lat": 21.7645, "lon": 72.1519},
    {"name": "Jamnagar", "state": "Gujarat", "lat": 22.4707, "lon": 70.0577},
    {"name": "Junagadh", "state": "Gujarat", "lat": 21.5222, "lon": 70.4579},
    {"name": "Gandhinagar", "state": "Gujarat", "lat": 23.2156, "lon": 72.6369},
    {"name": "Nadiad", "state": "Gujarat", "lat": 22.6916, "lon": 72.8634},
    {"name": "Anand", "state": "Gujarat", "lat": 22.5645, "lon": 72.9289},
    {"name": "Morbi", "state": "Gujarat", "lat": 22.812, "lon": 70.8378},
    {"name": "Bharuch", "state": "Gujarat", "lat": 21.7051, "lon": 72.9959},
    {"name": "Navsari", "state": "Gujarat", "lat": 20.9467, "lon": 72.952},
    {"name": "Porbandar", "state": "Gujarat", "lat": 21.6417, "lon": 69.6293},
    {"name": "Bhuj", "state": "Gujarat", "lat": 23.242, "lon": 69.6669},
    {"name": "Jaipur", "state": "Rajasthan", "lat": 26.9124, "lon": 75.7873},
    {"name": "Jodhpur", "state": "Rajasthan", "lat": 26.2389, "lon": 73.0243},
    {"name": "Kota", "state": "Rajasthan", "lat": 25.2138, "lon": 75.8648},
    {"name": "Bikaner", "state": "Rajasthan", "lat": 28.0229, "lon": 73.3119},
    {"name": "Ajmer", "state": "Rajasthan", "lat": 26.4499, "lon": 74.6399},
    {"name": "Udaipur", "state": "Rajasthan", "lat": 24.5854, "lon": 73.7125},
    {"name": "Bhilwara", "state": "Rajasthan", "lat": 25.3407, "lon": 74.6313},
    {"name": "Alwar", "state": "Rajasthan", "lat": 27.553, "lon": 76.6346},
    {"name": "Bharatpur", "state": "Rajasthan", "lat": 27.2152, "lon": 77.503},
    {"name": "Sikar", "state": "Rajasthan", "lat": 27.6094, "lon": 75.1398},
    {"name": "Pali", "state": "Rajasthan", "lat": 25.7713, "lon": 73.3234},
    {"name": "Sri Ganganagar", "state": "Rajasthan", "lat": 29.9038, "lon": 73.8772},
    {"name": "Visakhapatnam", "state": "Andhra Pradesh", "lat": 17.6868, "lon": 83.2185},
    {"name": "Vijayawada", "state": "Andhra Pradesh", "lat": 16.5062, "lon": 80.648},
    {"name": "Guntur", "state": "Andhra Pradesh", "lat": 16.3067, "lon": 80.4365},
    {"name": "Nellore", "state": "Andhra Pradesh", "lat": 14.4426, "lon": 79.9865},
    {"name": "Kurnool", "state": "Andhra Pradesh", "lat": 15.8281, "lon": 78.0373},
    {"name": "Rajahmundry", "state": "Andhra Pradesh", "lat": 17.0005, "lon": 81.804},
    {"name": "Tirupati", "state": "Andhra Pradesh", "lat": 13.6288, "lon": 79.4192},
    {"name": "Kakinada", "state": "Andhra Pradesh", "lat": 16.9891, "lon": 82.2475},
    {"name": "Kadapa", "state": "Andhra Pradesh", "lat": 14.4673, "lon": 78.8242},
    {"name": "Anantapur", "state": "Andhra Pradesh", "lat": 14.6819, "lon": 77.6006},
    {"name": "Eluru", "state": "Andhra Pradesh", "lat": 16.7107, "lon": 81.0952},
    {"name": "Ongole", "state": "Andhra Pradesh", "lat": 15.5057, "lon": 80.0499},
    {"name": "Hyderabad", "state": "Telangana", "lat": 17.385, "lon": 78.4867},
    {"name": "Warangal", "state": "Telangana", "lat": 17.9689, "lon": 79.5941},
    {"name": "Nizamabad", "state": "Telangana", "lat": 18.6725, "lon": 78.0941},
    {"name": "Karimnagar", "state": "Telangana", "lat": 18.4386, "lon": 79.1288},
    {"name": "Ramagundam", "state": "Telangana", "lat": 18.7551, "lon": 79.5144},
    {"name": "Khammam", "state": "Telangana", "lat": 17.2473, "lon": 80.1514},
    {"name": "Mahbubnagar", "state": "Telangana", "lat": 16.7488, "lon": 77.9856},
    {"name": "Nalgonda", "state": "Telangana", "lat": 17.0575, "lon": 79.2684},
    {"name": "Adilabad", "state": "Telangana", "lat": 19.6641, "lon": 78.532},
    {"name": "Suryapet", "state": "Telangana", "lat": 17.1439, "lon": 79.6239},
    {"name": "Thiruvananthapuram", "state": "Kerala", "lat": 8.5241, "lon": 76.9366},
    {"name": "Kochi", "state": "Kerala", "lat": 9.9312, "lon": 76.2673},
    {"name": "Kozhikode", "state": "Kerala", "lat": 11.2588, "lon": 75.7804},
    {"name": "Kollam", "state": "Kerala", "lat": 8.8932, "lon": 76.6141},
    {"name": "Thrissur", "state": "Kerala", "lat": 10.5276, "lon": 76.2144},
    {"name": "Alappuzha", "state": "Kerala", "lat": 9.4981, "lon": 76.3388},
    {"name": "Palakkad", "state": "Kerala", "lat": 10.7867, "lon": 76.6548},
    {"name": "Malappuram", "state": "Kerala", "lat": 11.0732, "lon": 76.074},
    {"name": "Kannur", "state": "Kerala", "lat": 11.8745, "lon": 75.3704},
    {"name": "Kottayam", "state": "Kerala", "lat": 9.5916, "lon": 76.5222},
    {"name": "Wayanad", "state": "Kerala", "lat": 11.6854, "lon": 76.132},
    {"name": "Idukki", "state": "Kerala", "lat": 9.8494, "lon": 76.9806},
    {"name": "Pathanamthitta", "state": "Kerala", "lat": 9.2648, "lon": 76.787},
    {"name": "Kasaragod", "state": "Kerala", "lat": 12.5102, "lon": 74.9852},
    {"name": "Indore", "state": "Madhya Pradesh", "lat": 22.7196, "lon": 75.8577},
    {"name": "Bhopal", "state": "Madhya Pradesh", "lat": 23.2599, "lon": 77.4126},
    {"name": "Jabalpur", "state": "Madhya Pradesh", "lat": 23.1815, "lon": 79.9864},
    {"name": "Gwalior", "state": "Madhya Pradesh", "lat": 26.2183, "lon": 78.1828},
    {"name": "Ujjain", "state": "Madhya Pradesh", "lat": 23.1765, "lon": 75.7885},
    {"name": "Sagar", "state": "Madhya Pradesh", "lat": 23.8388, "lon": 78.7378},
    {"name": "Dewas", "state": "Madhya Pradesh", "lat": 22.9676, "lon": 76.0534},
    {"name": "Satna", "state": "Madhya Pradesh", "lat": 24.6005, "lon": 80.8322},
    {"name": "Ratlam", "state": "Madhya Pradesh", "lat": 23.3315, "lon": 75.0367},
    {"name": "Rewa", "state": "Madhya Pradesh", "lat": 24.5362, "lon": 81.3037},
    {"name": "Chandigarh", "state": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    {"name": "Ludhiana", "state": "Punjab", "lat": 30.901, "lon": 75.8573},
    {"name": "Amritsar", "state": "Punjab", "lat": 31.634, "lon": 74.8723},
    {"name": "Jalandhar", "state": "Punjab", "lat": 31.326, "lon": 75.5762},
    {"name": "Patiala", "state": "Punjab", "lat": 30.3398, "lon": 76.3869},
    {"name": "Bathinda", "state": "Punjab", "lat": 30.211, "lon": 74.9455},
    {"name": "Pathankot", "state": "Punjab", "lat": 32.2689, "lon": 75.6499},
    {"name": "Hoshiarpur", "state": "Punjab", "lat": 31.5273, "lon": 75.9149},
    {"name": "Panipat", "state": "Haryana", "lat": 29.3909, "lon": 76.9635},
    {"name": "Ambala", "state": "Haryana", "lat": 30.3782, "lon": 76.7767},
    {"name": "Yamunanagar", "state": "Haryana", "lat": 30.129, "lon": 77.2674},
    {"name": "Rohtak", "state": "Haryana", "lat": 28.8955, "lon": 76.6066},
    {"name": "Hisar", "state": "Haryana", "lat": 29.1492, "lon": 75.7217},
    {"name": "Karnal", "state": "Haryana", "lat": 29.6857, "lon": 76.9905},
    {"name": "Bhubaneswar", "state": "Odisha", "lat": 20.2961, "lon": 85.8245},
    {"name": "Cuttack", "state": "Odisha", "lat": 20.4625, "lon": 85.8828},
    {"name": "Rourkela", "state": "Odisha", "lat": 22.2604, "lon": 84.8536},
    {"name": "Brahmapur", "state": "Odisha", "lat": 19.3149, "lon": 84.7941},
    {"name": "Sambalpur", "state": "Odisha", "lat": 21.4669, "lon": 83.9812},
    {"name": "Puri", "state": "Odisha", "lat": 19.8135, "lon": 85.8312},
    {"name": "Balasore", "state": "Odisha", "lat": 21.4934, "lon": 86.9135},
    {"name": "Bhadrak", "state": "Odisha", "lat": 21.0544, "lon": 86.4955},
    {"name": "Baripada", "state": "Odisha", "lat": 21.9347, "lon": 86.7369},
    {"name": "Guwahati", "state": "Assam", "lat": 26.1445, "lon": 91.7362},
    {"name": "Silchar", "state": "Assam", "lat": 24.8333, "lon": 92.7789},
    {"name": "Dibrugarh", "state": "Assam", "lat": 27.4728, "lon": 94.912},
    {"name": "Jorhat", "state": "Assam", "lat": 26.7509, "lon": 94.2037},
    {"name": "Nagaon", "state": "Assam", "lat": 26.3452, "lon": 92.684},
    {"name": "Tinsukia", "state": "Assam", "lat": 27.4922, "lon": 95.3537},
    {"name": "Tezpur", "state": "Assam", "lat": 26.6528, "lon": 92.7926},
    {"name": "Kaziranga", "state": "Assam", "lat": 26.5775, "lon": 93.1711},
    {"name": "Shillong", "state": "Meghalaya", "lat": 25.5788, "lon": 91.8933},
    {"name": "Cherrapunji", "state": "Meghalaya", "lat": 25.2702, "lon": 91.7323},
    {"name": "Mawsynram", "state": "Meghalaya", "lat": 25.2975, "lon": 91.5824},
    {"name": "Agartala", "state": "Tripura", "lat": 23.8315, "lon": 91.2868},
    {"name": "Aizawl", "state": "Mizoram", "lat": 23.7271, "lon": 92.7176},
    {"name": "Imphal", "state": "Manipur", "lat": 24.817, "lon": 93.9368},
    {"name": "Kohima", "state": "Nagaland", "lat": 25.6751, "lon": 94.1086},
    {"name": "Dimapur", "state": "Nagaland", "lat": 25.9068, "lon": 93.7271},
    {"name": "Itanagar", "state": "Arunachal", "lat": 27.0844, "lon": 93.6053},
    {"name": "Gangtok", "state": "Sikkim", "lat": 27.3314, "lon": 88.6138},
    {"name": "Srinagar", "state": "J&K", "lat": 34.0837, "lon": 74.7973},
    {"name": "Jammu", "state": "J&K", "lat": 32.7266, "lon": 74.857},
    {"name": "Anantnag", "state": "J&K", "lat": 33.7311, "lon": 75.1522},
    {"name": "Baramulla", "state": "J&K", "lat": 34.198, "lon": 74.3639},
    {"name": "Leh", "state": "Ladakh", "lat": 34.1526, "lon": 77.5771},
    {"name": "Shimla", "state": "Himachal", "lat": 31.1048, "lon": 77.1734},
    {"name": "Mandi", "state": "Himachal", "lat": 31.7087, "lon": 76.932},
    {"name": "Kullu", "state": "Himachal", "lat": 31.9579, "lon": 77.1095},
    {"name": "Manali", "state": "Himachal", "lat": 32.2432, "lon": 77.1892},
    {"name": "Dharamshala", "state": "Himachal", "lat": 32.219, "lon": 76.3234},
    {"name": "Solan", "state": "Himachal", "lat": 30.9084, "lon": 77.0999},
    {"name": "Dehradun", "state": "Uttarakhand", "lat": 30.3165, "lon": 78.0322},
    {"name": "Haridwar", "state": "Uttarakhand", "lat": 29.9457, "lon": 78.1642},
    {"name": "Rishikesh", "state": "Uttarakhand", "lat": 30.0869, "lon": 78.2676},
    {"name": "Nainital", "state": "Uttarakhand", "lat": 29.3919, "lon": 79.4542},
    {"name": "Haldwani", "state": "Uttarakhand", "lat": 29.2183, "lon": 79.513},
    {"name": "Roorkee", "state": "Uttarakhand", "lat": 29.8543, "lon": 77.888},
    {"name": "Ranchi", "state": "Jharkhand", "lat": 23.3441, "lon": 85.3096},
    {"name": "Jamshedpur", "state": "Jharkhand", "lat": 22.8046, "lon": 86.2029},
    {"name": "Dhanbad", "state": "Jharkhand", "lat": 23.7957, "lon": 86.4304},
    {"name": "Bokaro", "state": "Jharkhand", "lat": 23.6693, "lon": 86.1511},
    {"name": "Deoghar", "state": "Jharkhand", "lat": 24.4826, "lon": 86.7001},
    {"name": "Hazaribagh", "state": "Jharkhand", "lat": 23.9925, "lon": 85.3637},
    {"name": "Raipur", "state": "Chhattisgarh", "lat": 21.2514, "lon": 81.6296},
    {"name": "Bhilai", "state": "Chhattisgarh", "lat": 21.2144, "lon": 81.3788},
    {"name": "Bilaspur", "state": "Chhattisgarh", "lat": 22.0797, "lon": 82.1409},
    {"name": "Korba", "state": "Chhattisgarh", "lat": 22.3595, "lon": 82.7501},
    {"name": "Jagdalpur", "state": "Chhattisgarh", "lat": 19.074, "lon": 82.008},
    {"name": "Panaji", "state": "Goa", "lat": 15.4909, "lon": 73.8278},
    {"name": "Margao", "state": "Goa", "lat": 15.2832, "lon": 73.9862},
    {"name": "Vasco da Gama", "state": "Goa", "lat": 15.3982, "lon": 73.8113},
    {"name": "Puducherry", "state": "Puducherry", "lat": 11.9416, "lon": 79.8083},
    {"name": "Port Blair", "state": "Andaman", "lat": 11.6234, "lon": 92.7265},
    {"name": "Silvassa", "state": "DNH and DD", "lat": 20.2763, "lon": 73.0083},
    {"name": "Daman", "state": "DNH and DD", "lat": 20.3974, "lon": 72.8328},
]


def _fetch_city(city):
    """Fetch weather from Open-Meteo and run flood prediction for one city."""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": city["lat"],
            "longitude": city["lon"],
            "current": "temperature_2m,precipitation,windspeed_10m,cloudcover,relativehumidity_2m",
            "daily": "temperature_2m_max",
            "timezone": "auto",
            "forecast_days": 1,
        }
        resp = req_lib.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data["current"]
        daily = data["daily"]

        weather_data = {
            "temp":     current["temperature_2m"],
            "max_temp": daily["temperature_2m_max"][0],
            "wind":     current["windspeed_10m"],
            "cloud":    current["cloudcover"],
            "precip":   current["precipitation"],
            "humidity": current["relativehumidity_2m"],
        }

        label, confidence, _ = predict_flood(weather_data)

        # risk_pct = probability of FLOOD (0-100)
        if label == "Unsafe":
            risk_pct = round(confidence, 1)
        else:
            risk_pct = round(100 - confidence, 1)

        if risk_pct > 65:
            risk_label = "HIGH"
        elif risk_pct >= 35:
            risk_label = "MODERATE"
        else:
            risk_label = "SAFE"

        return {
            "name":     city["name"],
            "state":    city.get("state", "India"),
            "lat":      city["lat"],
            "lon":      city["lon"],
            "risk_pct": risk_pct,
            "label":    risk_label,
            "temp":     weather_data["temp"],
            "precip":   weather_data["precip"],
            "humidity": weather_data["humidity"],
            "wind":     weather_data["wind"],
            "cloud":    weather_data["cloud"],
        }
    except Exception:
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    prediction = None
    confidence = None
    weather_data = None
    individual_probs = None

    error_message = None

    if request.method == 'POST':
        mode = request.form.get('mode', 'live')
        if mode == 'simulation':
            city = request.form.get('city', 'Simulated Scenario')
            try:
                def safe_float(val, default):
                    try:
                        return float(val) if val not in (None, '') else default
                    except (ValueError, TypeError):
                        return default

                weather_data = {
                    "city": city,
                    "temp": safe_float(request.form.get('sim_temp'), 30.0),
                    "max_temp": safe_float(request.form.get('sim_max_temp'), 32.0),
                    "wind": safe_float(request.form.get('sim_wind'), 15.0),
                    "cloud": safe_float(request.form.get('sim_cloud'), 20.0),
                    "precip": safe_float(request.form.get('sim_precip'), 0.0),
                    "humidity": safe_float(request.form.get('sim_humidity'), 45.0),
                }
                prediction, confidence, individual_probs = predict_flood(weather_data)
            except Exception as e:
                error_message = f"Simulation error: {e}"
        else:
            city = request.form.get('city', '').strip()
            if not city:
                error_message = "Please enter a valid city or district name."
            else:
                try:
                    weather_data = get_city_weather(city)
                    prediction, confidence, individual_probs = predict_flood(weather_data)
                except Exception:
                    error_message = f"Could not find weather data for '{city}'. Please check the spelling and enter a valid city or district."
    return render_template('predict.html', 
                         prediction=prediction, 
                         confidence=confidence, 
                         weather=weather_data,
                         individual_probs=individual_probs,
                         error_message=error_message)

@app.route('/map')
def map_view():
    return render_template('riskmap.html')

@app.route('/map_data')
def map_data():
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(_fetch_city, city) for city in CITIES]
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
    return jsonify(results)

if __name__ == '__main__':
    import logging
    import flask.cli

    flask.cli.show_server_banner = lambda *_: None
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    print(" * Running on http://127.0.0.1:5000", flush=True)
    app.run(debug=False)
