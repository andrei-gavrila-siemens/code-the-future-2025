import React from 'react';
import {
  Facebook,
  Instagram,
  Twitter,
  Linkedin,
  Mail,
  Phone,
  MapPin,
  ShieldCheck,
  Truck,
  Info,
} from 'lucide-react';

const Footer = () => {
  return (
    <footer className="border-t px-6 py-10">
      <div className="max-w-6xl mx-auto grid gap-10 sm:grid-cols-2 md:grid-cols-4">
        {/* Brand */}
        <div>
          <h2 className="text-2xl font-bold mb-4">CUBURI</h2>
          <p className="text-sm mb-4">
            Unique educational toy cubes. Designed for creativity, crafted for fun.
          </p>
          <p className="text-xs text-gray-500">© {new Date().getFullYear()} CONA IT Solutions</p>
        </div>

        {/* Shop */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Shop</h3>
          <ul className="space-y-2 text-sm">
            <li><a href="/products" className="hover:underline">All Products</a></li>
            <li><a href="#" className="hover:underline">Categories</a></li>
            <li><a href="/" className="hover:underline">New Arrivals</a></li>
            <li><a href="#" className="hover:underline">Best Sellers</a></li>
          </ul>
        </div>

        {/* Customer Service */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Support</h3>
          <ul className="space-y-2 text-sm">
            <li><a href="#" className="hover:underline flex items-center gap-2"><Mail size={16} />Contact Us</a></li>
            <li><a href="#" className="hover:underline flex items-center gap-2"><Truck size={16} />Shipping & Delivery</a></li>
            <li><a href="#" className="hover:underline flex items-center gap-2"><ShieldCheck size={16} />Returns & Refunds</a></li>
            <li><a href="#" className="hover:underline flex items-center gap-2"><Info size={16} />FAQs</a></li>
          </ul>
        </div>

        {/* Contact + Socials */}
        <div>
          <h3 className="text-lg font-semibold mb-3">Connect</h3>
          <ul className="space-y-2 text-sm mb-4">
            <li className="flex items-center gap-2"><Phone size={16} /> +40 123 456 789</li>
            <li className="flex items-center gap-2"><Mail size={16} /> support@cuburi.com</li>
            <li className="flex items-center gap-2"><MapPin size={16} /> Brasov, Romania</li>
          </ul>
          <div className="flex gap-4">
            <a href="https://facebook.com" target="_blank" rel="noreferrer"><Facebook size={20} /></a>
            <a href="https://instagram.com" target="_blank" rel="noreferrer"><Instagram size={20} /></a>
            <a href="https://twitter.com" target="_blank" rel="noreferrer"><Twitter size={20} /></a>
            <a href="https://linkedin.com" target="_blank" rel="noreferrer"><Linkedin size={20} /></a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
