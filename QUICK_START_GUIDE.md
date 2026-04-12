# SheSecure - Quick Start Guide

## ✅ Your App is Ready!

The SheSecure application is now fully functional with a complete login/signup system, database, and all features working.

---

## 🚀 How to Start the Application

### Option 1: Easy Start (Windows) - **RECOMMENDED**
Double-click the file:
```
START_SheSecure.bat
```

The app will launch and you'll see:
```
🔗 Access the application at: http://localhost:5000
```

### Option 2: Using Python Directly
Run this command in the terminal (when in the she-secure folder):
```bash
python run_app.py
```

---

## 📱 Accessing the Application

1. **On Your Computer:**
   - Open Chrome (or any browser)
   - Go to: `http://localhost:5000`

2. **On Other Devices (Same Network):**
   - Open Chrome
   - Go to: `http://YOUR_COMPUTER_IP:5000`
   - Find your IP in the server startup message

---

## 👤 User Registration & Login

### First Time Users - Create an Account
1. Click **"Sign up here"** or go to signup page
2. Enter:
   - **Username**: 3-20 characters (letters, numbers, underscores)
   - **Email**: Valid email address
   - **Password**: At least 6 characters
   - **Confirm Password**: Must match password
3. Click **Create Account**
4. You'll be redirected to login page
5. Login with your new credentials

### Existing Users - Login
1. Enter your **Username**
2. Enter your **Password**
3. Click **Enter Dashboard**

---

## 🎯 Features After Login

Once logged in, you can access:
- **Dashboard**: Main control center
- **Location**: Live map and safer travel planner
- **Crime Data**: Analytics and hotspot analysis
- **Helplines**: Emergency contacts and support
- **Predictor**: Safety risk predictor
- **Chatbot**: AI safety assistant
- **Counselling**: Support services
- **Emergency**: SOS tools and offline support

---

## 🔧 Database Information

- **Type**: SQLite
- **Location**: `instance/site.db`
- **Auto-Created**: Yes, happens on first run
- **Users Table**: Stores encrypted passwords

---

## 🛡️ Security Features

✅ Passwords are encrypted using PBKDF2:SHA256  
✅ Session management with Flask-Login  
✅ Protected routes require authentication  
✅ Input validation on all forms  
✅ CSRF protection ready  

---

## 🌐 Website Structure

```
SheSecure/
├── app.py                 (Main Flask app)
├── run_app.py            (Startup script)
├── START_SheSecure.bat   (Windows launcher)
├── requirements.txt      (Python dependencies)
├── static/               (CSS/JS/Images)
│   ├── style.css
│   ├── animations.css
│   └── js/
├── templates/            (HTML pages)
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   └── ... (other pages)
└── instance/
    └── site.db          (Database file)
```

---

## 🐛 Troubleshooting

### Issue: "Address already in use"
**Solution**: Port 5000 is already in use. Kill the process:
```bash
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F
```

### Issue: "ModuleNotFoundError"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Database errors
**Solution**: Delete `instance/site.db` and restart the app. It will recreate the database.

### Issue: Can't access from another device
**Solution**: 
- Make sure both devices are on the same network
- Use the IP shown in startup message instead of localhost
- Check if firewall is blocking port 5000

---

## 📝 Test Credentials

You can create test accounts with any username/email/password combination following the validation rules:
- Username: 3-20 characters
- Email: Valid format (contains @)
- Password: At least 6 characters

---

## 💡 Tips for Best Experience

1. **Use Chrome or Firefox** for best compatibility
2. **Keep the terminal window open** while using the app (it shows debug info)
3. **Offline Mode**: Some features work offline with localStorage
4. **Live Location**: Enable location access when prompted for full features
5. **Mobile Friendly**: Works well on mobile browsers too!

---

## 🔌 Server Details

- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 5000
- **Debug Mode**: Enabled (for development)
- **Auto-Reload**: Enabled (changes reload automatically)

---

## 📞 Need Help?

All the core functionality is working:
- ✅ User registration
- ✅ User login/logout
- ✅ Password encryption
- ✅ Session management
- ✅ Database persistence
- ✅ All routes protected

**The app is production-ready for local testing!**

---

**Happy using SheSecure! Stay Safe! 🛡️**
