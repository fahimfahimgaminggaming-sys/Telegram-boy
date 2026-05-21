// servconst express = require('express');
const { MongoClient } = require('mongodb');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

// static files serving
app.use(express.static(path.join(__dirname, 'public')));

// config
const MONGO_URI = "mongodb+srv://fahim:Fahim123456@cluster0.3sihfnt.mongodb.net/?retryWrites=true&w=majority";
const DB_NAME = "premium_service_bot";
const ADMIN_EMAIL = "fahimfahimf737@gmail.com";
const ADMIN_ID = 7015857680;

let db, users, services, serviceItems, purchases, deposits, counters, settings, bannedUsers;

// Database Connection
MongoClient.connect(MONGO_URI)
  .then(client => {
    db = client.db(DB_NAME);
    users = db.collection("users");
    services = db.collection("services");
    serviceItems = db.collection("service_items");
    purchases = db.collection("purchases");
    deposits = db.collection("deposits");
    counters = db.collection("counters");
    settings = db.collection("settings");
    bannedUsers = db.collection("banned_users");
    console.log("🟢 Connected to MongoDB Atlas Successfully!");
  })
  .catch(err => console.error("🔴 MongoDB Connection Error:", err));

// Helpers
function nowText() {
  const d = new Date();
  return `${d.getHours()}:${d.getMinutes()} | ${d.getDate()}-${d.getMonth()+1}-${d.getFullYear()}`;
}

async function getNextSequence(name) {
  const counter = await counters.findOneAndUpdate(
    { _id: name },
    { $inc: { seq: 1 } },
    { upsert: true, returnDocument: 'after' }
  );
  return counter.seq;
}

// Middleware to Check Maintenance & Ban Status
async function checkStatus(req, res, next) {
  const userId = parseInt(req.headers['user-id']);
  const isAdmin = req.headers['is-admin'] === 'true';

  if (!isAdmin && userId) {
    // Check Ban
    const ban = await bannedUsers.findOne({ user_id: userId });
    if (ban) return res.status(403).json({ error: `You are banned! Reason: ${ban.reason || 'No reason'}` });

    // Check Maintenance
    const maintenance = await settings.findOne({ key: "maintenance_mode" });
    if (maintenance && maintenance.value === true) {
      return res.status(503).json({ error: "Site is under maintenance. Please try again later." });
    }
  }
  next();
}

// ---------------- USER ENDPOINTS ----------------

// User Login / Registration lookup
app.post('/api/auth', async (req, res) => {
  const { email, password, userId } = req.body;

  // Admin login check
  if (email === ADMIN_EMAIL) {
    return res.json({ success: true, isAdmin: true, user: { user_id: ADMIN_ID, username: "Admin_Fahim", balance: 9999 } });
  }

  // Web user lookup using Telegram User ID
  if (userId) {
    const uId = parseInt(userId);
    let user = await users.findOne({ user_id: uId });
    if (!user) {
      // Auto register user if not found
      user = {
        user_id: uId,
        username: "WebUser_" + uId,
        balance: 0.0,
        bought_count: 0,
        total_deposit: 0.0,
        total_spent: 0.0,
        created_at: nowText(),
        updated_at: nowText()
      };
      await users.insertOne(user);
    }
    return res.json({ success: true, isAdmin: false, user });
  }
  return res.status(400).json({ error: "Invalid credentials or User ID" });
});

// Get User Profile Data
app.get('/api/profile/:userId', checkStatus, async (req, res) => {
  const user = await users.findOne({ user_id: parseInt(req.params.userId) });
  if (!user) return res.status(404).json({ error: "User not found" });
  res.json(user);
});

// View Active Services
app.get('/api/services', checkStatus, async (req, res) => {
  const activeServices = await services.find({ is_active: true }).sort({ service_id: -1 }).toArray();
  res.json(activeServices);
});

// Buy Service (Atomic Operation matching Python code)
app.post('/api/buy', checkStatus, async (req, res) => {
  const { userId, serviceId } = req.body;
  const uId = parseInt(userId);
  const sId = parseInt(serviceId);

  const user = await users.findOne({ user_id: uId });
  const service = await services.findOne({ service_id: sId });

  if (!user || !service) return res.status(404).json({ error: "User or Service not found" });
  if (service.stock <= 0 || !service.is_active) return res.status(400).json({ error: "Product out of stock or inactive" });
  if (user.balance < service.price) return res.status(400).json({ error: "Insufficient Balance" });

  // Get available item and mark as sold instantly
  const item = await serviceItems.findOneAndUpdate(
    { service_id: sId, is_sold: 0 },
    { $set: { is_sold: 1, sold_at: nowText() } },
    { sort: { item_id: 1 }, returnDocument: 'after' }
  );

  if (!item) return res.status(400).json({ error: "No available account item found in stock" });

  // Deduct balance and update user stats
  await users.updateOne(
    { user_id: uId },
    { 
      $inc: { balance: -parseFloat(service.price), total_spent: parseFloat(service.price), bought_count: 1 },
      $set: { updated_at: nowText() }
    }
  );

  // Decrement Stock
  await services.updateOne(
    { service_id: sId },
    { $inc: { stock: -1 }, $set: { updated_at: nowText() } }
  );

  // Save Purchase history
  const purchaseId = await getNextSequence("purchase_id");
  const purchaseDoc = {
    purchase_id: purchaseId,
    user_id: uId,
    username: user.username,
    product_name: service.name,
    product_price: parseFloat(service.price),
    product_gmail: item.gmail,
    product_password: item.password,
    created_at: nowText()
  };
  await purchases.insertOne(purchaseDoc);

  res.json({ success: true, item: purchaseDoc });
});

// View User Orders
app.get('/api/orders/:userId', checkStatus, async (req, res) => {
  const history = await purchases.find({ user_id: parseInt(req.params.userId) }).sort({ purchase_id: -1 }).toArray();
  res.json(history);
});

// Submit Deposit Request
app.post('/api/deposit', checkStatus, async (req, res) => {
  const { userId, username, amount, method, trxInfo } = req.body;
  const depositId = await getNextSequence("deposit_id");

  const depositDoc = {
    deposit_id: depositId,
    user_id: parseInt(userId),
    username: username || "WebUser",
    amount: parseFloat(amount),
    payment_method: method,
    screenshot_file_id: trxInfo || "Web Submission", // Using transaction hash/reference as proof
    status: "pending",
    created_at: nowText()
  };

  await deposits.insertOne(depositDoc);
  res.json({ success: true, depositId });
});


// ---------------- ADMIN ENDPOINTS ----------------

// Site Stats
app.get('/api/admin/stats', async (req, res) => {
  const totalUsers = await users.countDocuments({});
  const totalDeps = await deposits.countDocuments({});
  const pendingDeps = await deposits.countDocuments({ status: "pending" });
  const maintenance = await settings.findOne({ key: "maintenance_mode" });
  
  res.json({
    totalUsers,
    totalDeposits: totalDeps,
    pendingDeposits: pendingDeps,
    maintenanceMode: maintenance ? maintenance.value : false
  });
});

// Get Pending Deposits
app.get('/api/admin/pending-deposits', async (req, res) => {
  const list = await deposits.find({ status: "pending" }).sort({ deposit_id: -1 }).toArray();
  res.json(list);
});

// Action on Deposit (Confirm / Reject)
app.post('/api/admin/action-deposit', async (req, res) => {
  const { depositId, action } = req.body;
  const dep = await deposits.findOne({ deposit_id: parseInt(depositId) });

  if (!dep || dep.status !== 'pending') return res.status(404).json({ error: "Pending deposit not found" });

  if (action === 'confirm') {
    await deposits.updateOne({ deposit_id: dep.deposit_id }, { $set: { status: "confirmed", updated_at: nowText() } });
    await users.updateOne({ user_id: dep.user_id }, { 
      $inc: { balance: parseFloat(dep.amount), total_deposit: parseFloat(dep.amount) },
      $set: { updated_at: nowText() }
    });
  } else {
    await deposits.updateOne({ deposit_id: dep.deposit_id }, { $set: { status: "rejected", updated_at: nowText() } });
  }
  res.json({ success: true });
});

// Service Management (Add Service)
app.post('/api/admin/add-service', async (req, res) => {
  const { name, price, category, description } = req.body;
  const serviceId = await getNextSequence("service_id");

  const newService = {
    service_id: serviceId,
    name,
    price: parseFloat(price),
    category: category || "General",
    description: description || "No description",
    stock: 0,
    is_active: true,
    created_at: nowText(),
    updated_at: nowText()
  };

  await services.insertOne(newService);
  res.json({ success: true, serviceId });
});

// Add Stock Items
app.post('/api/admin/add-stock', async (req, res) => {
  const { serviceId, gmail, password } = req.body;
  const sId = parseInt(serviceId);

  const existingItem = await serviceItems.findOne({ service_id: sId, gmail });
  if (existingItem) return res.status(400).json({ error: "This Account/Gmail already exists in stock!" });

  const itemId = await getNextSequence("item_id");
  await serviceItems.insertOne({
    item_id: itemId,
    service_id: sId,
    gmail,
    password,
    is_sold: 0,
    created_at: nowText()
  });

  await services.updateOne({ service_id: sId }, { $inc: { stock: 1 }, $set: { updated_at: nowText() } });
  res.json({ success: true });
});

// Delete Service completely
app.delete('/api/admin/delete-service/:id', async (req, res) => {
  const sId = parseInt(req.params.id);
  await services.deleteOne({ service_id: sId });
  await serviceItems.deleteMany({ service_id: sId });
  res.json({ success: true });
});

// Toggle Service Active Status
app.post('/api/admin/toggle-service', async (req, res) => {
  const { serviceId } = req.body;
  const sId = parseInt(serviceId);
  const service = await services.findOne({ service_id: sId });
  if (!service) return res.status(404).json({ error: "Service not found" });

  const nextStatus = !service.is_active;
  await services.updateOne({ service_id: sId }, { $set: { is_active: nextStatus, updated_at: nowText() } });
  res.json({ success: true, is_active: nextStatus });
});

// Toggle Maintenance System
app.post('/api/admin/toggle-maintenance', async (req, res) => {
  const maintenance = await settings.findOne({ key: "maintenance_mode" });
  const currentStatus = maintenance ? maintenance.value : false;
  const newStatus = !currentStatus;

  await settings.updateOne(
    { key: "maintenance_mode" },
    { $set: { value: newStatus, updated_at: nowText() } },
    { upsert: true }
  );
  res.json({ success: true, maintenanceMode: newStatus });
});

// Ban/Unban System
app.post('/api/admin/toggle-ban', async (req, res) => {
  const { userId, reason, action } = req.body;
  const uId = parseInt(userId);

  if (action === 'ban') {
    await bannedUsers.updateOne({ user_id: uId }, { $set: { reason, created_at: nowText() } }, { upsert: true });
  } else {
    await bannedUsers.deleteOne({ user_id: uId });
  }
  res.json({ success: true });
});

// Fallback Route to Frontend
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Server Listen
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`🚀 Server fully operational on port ${PORT}`));
        er.js Premium Web Hub operational on port ${PORT}`));
  
