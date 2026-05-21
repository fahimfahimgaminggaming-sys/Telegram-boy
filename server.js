// server.js
const express = require('express');
const mongoose = require('mongoose');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const cors = require('cors');
const path = require('path');

const app = express();
app.use(express.json());
app.use(cors());

// --- CONFIGURATION ---
const JWT_SECRET = 'fahim_pro_secret_key_2026';
const MONGO_URI = "mongodb+srv://fahim:Fahim123456@cluster0.3sihfnt.mongodb.net/premium_service_bot?retryWrites=true&w=majority";

// Requested Credentials
const ADMIN_EMAIL = 'fahimfahimf737@gmail.com';
const ADMIN_PASSWORD_RAW = '@FAHIM1UKBD1ST';

// Connect to your existing MongoDB Cluster
mongoose.connect(MONGO_URI)
  .then(() => console.log('🛡️ Database connected successfully to premium_service_bot'))
  .catch(err => console.error('Database connection error:', err));

// --- MONGOOSE SCHEMAS (Matching your Python setup) ---
const UserSchema = new mongoose.Schema({
  user_id: { type: Number, unique: true, required: true },
  username: { type: String, default: '' },
  balance: { type: Number, default: 0.0 },
  total_spent: { type: Number, default: 0.0 },
  bought_count: { type: Number, default: 0 },
  email: { type: String, unique: true, sparse: true },
  password: { type: String }, // Hashed
  is_admin: { type: Boolean, default: false }
});

const ServiceSchema = new mongoose.Schema({
  service_id: { type: Number, unique: true },
  name: String,
  price: Number,
  category: { type: String, default: 'General' },
  description: String,
  stock: { type: Number, default: 0 }
});

const ServiceItemSchema = new mongoose.Schema({
  service_id: Number,
  gmail: { type: String, required: true },
  password: { type: String, required: true },
  is_sold: { type: Boolean, default: false },
  sold_at: Date
});

const DepositSchema = new mongoose.Schema({
  deposit_id: { type: Number, unique: true },
  user_id: Number,
  username: String,
  amount: Number,
  payment_method: String,
  status: { type: String, default: 'pending' }, // pending, confirmed, rejected
  created_at: { type: Date, default: Date.now }
});

const PurchaseSchema = new mongoose.Schema({
  user_id: Number,
  product_name: String,
  price: Number,
  gmail: String,
  account_pass: String,
  created_at: { type: Date, default: Date.now }
});

const CounterSchema = new mongoose.Schema({
  _id: String,
  seq: { type: Number, default: 0 }
});

const User = mongoose.model('User', UserSchema, 'users');
const Service = mongoose.model('Service', ServiceSchema, 'services');
const ServiceItem = mongoose.model('ServiceItem', ServiceItemSchema, 'service_items');
const Deposit = mongoose.model('Deposit', DepositSchema, 'deposits');
const Purchase = mongoose.model('Purchase', PurchaseSchema, 'purchases');
const Counter = mongoose.model('Counter', CounterSchema, 'counters');

// Counter increment helper for Sequence IDs
async function getNextSequenceValue(sequenceName) {
  const sequenceDocument = await Counter.findByIdAndUpdate(
    sequenceName,
    { $inc: { seq: 1 } },
    { new: true, upsert: true }
  );
  return sequenceDocument.seq;
}

// Seed Primary Admin Account 
async function seedAdmin() {
  const adminExists = await User.findOne({ email: ADMIN_EMAIL });
  if (!adminExists) {
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(ADMIN_PASSWORD_RAW, salt);
    await User.create({
      user_id: 7015857680, // Matches your Python script ADMIN_ID
      username: 'FAHIM1UKBD1ST',
      email: ADMIN_EMAIL,
      password: hashedPassword,
      is_admin: true,
      balance: 10000.0
    });
    console.log('📌 Primary Admin Account Registered successfully.');
  }
}
seedAdmin();

// --- SECURITY MIDDLEWARE ---
function authenticateToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  if (!token) return res.status(401).json({ message: 'Authentication required' });

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.status(403).json({ message: 'Session expired. Please log in again.' });
    req.user = user;
    next();
  });
}

function requireAdmin(req, res, next) {
  if (!req.user || !req.user.is_admin) {
    return res.status(403).json({ message: 'Forbidden: Administrative clearance needed' });
  }
  next();
}

// --- API APPARATUS & ENDPOINTS ---

// Auth Systems
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await User.findOne({ email });
    if (!user) return res.status(404).json({ message: 'User not found' });

    const validPass = await bcrypt.compare(password, user.password);
    if (!validPass) return res.status(400).json({ message: 'Incorrect credentials' });

    const token = jwt.sign({ id: user._id, user_id: user.user_id, is_admin: user.is_admin, email: user.email }, JWT_SECRET, { expiresIn: '12h' });
    res.json({ token, is_admin: user.is_admin, username: user.username });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.post('/api/auth/register', async (req, res) => {
  const { email, password, username } = req.body;
  try {
    const exists = await User.findOne({ email });
    if (exists) return res.status(400).json({ message: 'Email already in use' });

    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);
    const mockTelegramId = Math.floor(100000000 + Math.random() * 900000000);

    await User.create({
      user_id: mockTelegramId,
      username: username || 'web_user',
      email,
      password: hashedPassword,
      is_admin: false
    });
    res.status(201).json({ message: 'Registration Successful' });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// App Engine Frontends
app.get('/api/profile', authenticateToken, async (req, res) => {
  const user = await User.findById(req.user.id).select('-password');
  res.json(user);
});

app.get('/api/services', authenticateToken, async (req, res) => {
  const services = await Service.find({});
  res.json(services);
});

app.post('/api/services/buy', authenticateToken, async (req, res) => {
  const { service_id } = req.body;
  const user = await User.findById(req.user.id);

  const service = await Service.findOne({ service_id });
  if (!service || service.stock <= 0) {
    return res.status(400).json({ message: 'Product completely out of stock!' });
  }

  if (user.balance < service.price) {
    return res.status(400).json({ message: 'Insufficient funds. Please fund your balance.' });
  }

  // Atomically grab an item
  const item = await ServiceItem.findOneAndUpdate(
    { service_id: service.service_id, is_sold: false },
    { $set: { is_sold: true, sold_at: new Date() } },
    { new: true }
  );

  if (!item) return res.status(400).json({ message: 'Stock sync failure. Try again.' });

  // Update user parameters
  user.balance -= service.price;
  user.total_spent += service.price;
  user.bought_count += 1;
  await user.save();

  // Deduct stock count safely
  service.stock -= 1;
  await service.save();

  const receipt = await Purchase.create({
    user_id: user.user_id,
    product_name: service.name,
    price: service.price,
    gmail: item.gmail,
    account_pass: item.password
  });

  res.json({ message: 'Purchase Complete!', purchase: receipt });
});

app.post('/api/deposits/submit', authenticateToken, async (req, res) => {
  const { amount, payment_method } = req.body;
  const nextDepId = await getNextSequenceValue('deposit_id');
  const user = await User.findById(req.user.id);

  const dep = await Deposit.create({
    deposit_id: nextDepId,
    user_id: user.user_id,
    username: user.username,
    amount: parseFloat(amount),
    payment_method
  });
  res.status(201).json({ message: 'Deposit requested successfully', deposit: dep });
});

app.get('/api/purchases', authenticateToken, async (req, res) => {
  const history = await Purchase.find({ user_id: req.user.user_id }).sort({ created_at: -1 });
  res.json(history);
});

// --- ADMIN LEVEL SYSTEM OVERRIDES ---
app.get('/api/admin/deposits/pending', authenticateToken, requireAdmin, async (req, res) => {
  const list = await Deposit.find({ status: 'pending' });
  res.json(list);
});

app.post('/api/admin/deposits/action', authenticateToken, requireAdmin, async (req, res) => {
  const { deposit_id, action } = req.body; // action: 'confirm' or 'reject'
  const dep = await Deposit.findOne({ deposit_id });
  if (!dep || dep.status !== 'pending') return res.status(400).json({ message: 'Deposit request already settled.' });

  if (action === 'confirm') {
    dep.status = 'confirmed';
    await User.findOneAndUpdate({ user_id: dep.user_id }, { $inc: { balance: dep.amount } });
  } else {
    dep.status = 'rejected';
  }
  await dep.save();
  res.json({ message: `Transaction set to ${dep.status}` });
});

app.post('/api/admin/services/create', authenticateToken, requireAdmin, async (req, res) => {
  const { name, price, category, description } = req.body;
  const nextSrvId = await getNextSequenceValue('service_id');
  const newSrv = await Service.create({ service_id: nextSrvId, name, price, category, description, stock: 0 });
  res.status(201).json(newSrv);
});

app.post('/api/admin/services/stock', authenticateToken, requireAdmin, async (req, res) => {
  const { service_id, gmail, password } = req.body;
  await ServiceItem.create({ service_id: parseInt(service_id), gmail, password });
  await Service.findOneAndUpdate({ service_id: parseInt(service_id) }, { $inc: { stock: 1 } });
  res.json({ message: 'Stock allocated.' });
});

// Bind frontend static distribution build assets
app.use(express.static(path.join(__dirname, 'public')));
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

const PORT = 5000;
app.listen(PORT, () => console.log(`🚀 Premium Web Hub operational on port ${PORT}`));
  
