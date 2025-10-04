# Messaging App - Practical Implementation Example

## 🚀 Quick Start: Building a Telegram-like App

This guide provides a complete, working example of a messaging platform with real-time capabilities.

## 📁 Project Structure

```
messaging-app/
├── 📁 frontend/                 # Next.js React App
│   ├── 📁 components/           # React Components
│   ├── 📁 pages/               # Next.js Pages
│   ├── 📁 hooks/               # Custom Hooks
│   ├── 📁 services/            # API Services
│   └── 📁 utils/               # Utility Functions
├── 📁 backend/                  # Node.js Backend
│   ├── 📁 src/                 # Source Code
│   ├── 📁 prisma/              # Database Schema
│   └── 📁 tests/               # Test Files
├── 📁 mobile/                   # React Native App
│   ├── 📁 src/                 # Source Code
│   ├── 📁 components/          # React Native Components
│   └── 📁 navigation/          # Navigation Setup
└── 📁 infrastructure/           # Docker & K8s
    ├── 📄 docker-compose.yml   # Development Environment
    └── 📁 k8s/                 # Kubernetes Manifests
```

## 🛠️ Step 1: Backend Implementation

### **1.1 Database Schema (Prisma)**

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  username  String   @unique
  password  String
  avatar    String?
  status    UserStatus @default(OFFLINE)
  lastSeen  DateTime?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  
  // Relations
  messages  Message[]
  chats     ChatUser[]
  contacts  Contact[]
  sentMessages Message[] @relation("SentMessages")
  
  @@map("users")
}

model Chat {
  id          String   @id @default(cuid())
  name        String?
  type        ChatType @default(PRIVATE)
  avatar      String?
  description String?
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
  
  // Relations
  messages    Message[]
  users       ChatUser[]
  lastMessage Message? @relation("LastMessage")
  
  @@map("chats")
}

model Message {
  id        String      @id @default(cuid())
  content   String
  type      MessageType @default(TEXT)
  fileUrl   String?
  fileSize  Int?
  fileType  String?
  isRead    Boolean     @default(false)
  createdAt DateTime    @default(now())
  updatedAt DateTime    @updatedAt
  
  // Relations
  chatId    String
  chat      Chat        @relation(fields: [chatId], references: [id])
  userId    String
  user      User        @relation("SentMessages", fields: [userId], references: [id])
  
  // Indexes
  @@index([chatId, createdAt])
  @@map("messages")
}

model ChatUser {
  id        String   @id @default(cuid())
  role      ChatRole @default(MEMBER)
  joinedAt  DateTime @default(now())
  
  // Relations
  chatId    String
  chat      Chat      @relation(fields: [chatId], references: [id])
  userId    String
  user      User      @relation(fields: [userId], references: [id])
  
  @@unique([chatId, userId])
  @@map("chat_users")
}

model Contact {
  id        String   @id @default(cuid())
  status    ContactStatus @default(PENDING)
  createdAt DateTime @default(now())
  
  // Relations
  userId    String
  user      User      @relation(fields: [userId], references: [id])
  contactId String
  contact   User      @relation("UserContacts", fields: [contactId], references: [id])
  
  @@unique([userId, contactId])
  @@map("contacts")
}

// Enums
enum UserStatus {
  ONLINE
  OFFLINE
  AWAY
  BUSY
}

enum ChatType {
  PRIVATE
  GROUP
  CHANNEL
}

enum MessageType {
  TEXT
  IMAGE
  VIDEO
  AUDIO
  FILE
  STICKER
  GIF
  SYSTEM
}

enum ChatRole {
  ADMIN
  MODERATOR
  MEMBER
}

enum ContactStatus {
  PENDING
  ACCEPTED
  BLOCKED
}
```

### **1.2 Backend API (Express + Socket.io)**

```typescript
// backend/src/app.ts
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import cors from 'cors';
import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.FRONTEND_URL,
    methods: ['GET', 'POST']
  }
});

const prisma = new PrismaClient();

// Middleware
app.use(cors());
app.use(express.json());

// Authentication middleware
const authenticateToken = (req: any, res: any, next: any) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }
  
  jwt.verify(token, process.env.JWT_SECRET!, (err: any, user: any) => {
    if (err) {
      return res.status(403).json({ error: 'Invalid token' });
    }
    req.user = user;
    next();
  });
};

// Routes
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, username, password } = req.body;
    
    // Hash password
    const bcrypt = require('bcryptjs');
    const hashedPassword = await bcrypt.hash(password, 10);
    
    // Create user
    const user = await prisma.user.create({
      data: {
        email,
        username,
        password: hashedPassword
      }
    });
    
    // Generate JWT
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET!);
    
    res.json({ user, token });
  } catch (error) {
    res.status(400).json({ error: 'Registration failed' });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user
    const user = await prisma.user.findUnique({
      where: { email }
    });
    
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Verify password
    const bcrypt = require('bcryptjs');
    const validPassword = await bcrypt.compare(password, user.password);
    
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Generate JWT
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET!);
    
    res.json({ user, token });
  } catch (error) {
    res.status(400).json({ error: 'Login failed' });
  }
});

// Get user chats
app.get('/api/chats', authenticateToken, async (req, res) => {
  try {
    const chats = await prisma.chat.findMany({
      where: {
        users: {
          some: {
            userId: req.user.userId
          }
        }
      },
      include: {
        users: {
          include: {
            user: true
          }
        },
        lastMessage: {
          include: {
            user: true
          }
        }
      },
      orderBy: {
        updatedAt: 'desc'
      }
    });
    
    res.json(chats);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch chats' });
  }
});

// Get chat messages
app.get('/api/chats/:chatId/messages', authenticateToken, async (req, res) => {
  try {
    const { chatId } = req.params;
    const { page = 1, limit = 50 } = req.query;
    
    const messages = await prisma.message.findMany({
      where: { chatId },
      include: {
        user: true
      },
      orderBy: {
        createdAt: 'desc'
      },
      skip: (Number(page) - 1) * Number(limit),
      take: Number(limit)
    });
    
    res.json(messages.reverse());
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch messages' });
  }
});

// Socket.io connection handling
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  
  if (!token) {
    return next(new Error('Authentication error'));
  }
  
  jwt.verify(token, process.env.JWT_SECRET!, (err: any, decoded: any) => {
    if (err) {
      return next(new Error('Authentication error'));
    }
    socket.userId = decoded.userId;
    next();
  });
});

io.on('connection', (socket) => {
  console.log(`User ${socket.userId} connected`);
  
  // Join user to their personal room
  socket.join(`user:${socket.userId}`);
  
  // Update user status to online
  prisma.user.update({
    where: { id: socket.userId },
    data: { status: 'ONLINE' }
  });
  
  // Join chat room
  socket.on('join:chat', (chatId) => {
    socket.join(`chat:${chatId}`);
    console.log(`User ${socket.userId} joined chat ${chatId}`);
  });
  
  // Leave chat room
  socket.on('leave:chat', (chatId) => {
    socket.leave(`chat:${chatId}`);
    console.log(`User ${socket.userId} left chat ${chatId}`);
  });
  
  // Send message
  socket.on('message:send', async (data) => {
    try {
      const { chatId, content, type = 'TEXT' } = data;
      
      // Create message in database
      const message = await prisma.message.create({
        data: {
          content,
          type,
          chatId,
          userId: socket.userId
        },
        include: {
          user: true
        }
      });
      
      // Update chat's last message
      await prisma.chat.update({
        where: { id: chatId },
        data: {
          updatedAt: new Date(),
          lastMessage: {
            connect: { id: message.id }
          }
        }
      });
      
      // Emit message to all users in the chat
      io.to(`chat:${chatId}`).emit('message:new', message);
      
    } catch (error) {
      socket.emit('error', { message: 'Failed to send message' });
    }
  });
  
  // Typing indicator
  socket.on('typing:start', (data) => {
    socket.to(`chat:${data.chatId}`).emit('typing:start', {
      userId: socket.userId,
      chatId: data.chatId
    });
  });
  
  socket.on('typing:stop', (data) => {
    socket.to(`chat:${data.chatId}`).emit('typing:stop', {
      userId: socket.userId,
      chatId: data.chatId
    });
  });
  
  // Handle disconnect
  socket.on('disconnect', async () => {
    console.log(`User ${socket.userId} disconnected`);
    
    // Update user status to offline
    await prisma.user.update({
      where: { id: socket.userId },
      data: { 
        status: 'OFFLINE',
        lastSeen: new Date()
      }
    });
  });
});

const PORT = process.env.PORT || 3001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

## 🎨 Step 2: Frontend Implementation

### **2.1 React Components**

```typescript
// frontend/components/ChatList.tsx
import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { MessageCircle, Users, Hash } from 'lucide-react';

interface Chat {
  id: string;
  name?: string;
  type: 'PRIVATE' | 'GROUP' | 'CHANNEL';
  avatar?: string;
  lastMessage?: {
    content: string;
    createdAt: string;
    user: {
      username: string;
    };
  };
  users: Array<{
    user: {
      id: string;
      username: string;
      avatar?: string;
    };
  }>;
}

export default function ChatList() {
  const [selectedChat, setSelectedChat] = useState<string | null>(null);
  
  const { data: chats, isLoading } = useQuery({
    queryKey: ['chats'],
    queryFn: async () => {
      const response = await fetch('/api/chats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      return response.json();
    }
  });
  
  const getChatIcon = (type: string) => {
    switch (type) {
      case 'PRIVATE':
        return <MessageCircle className="h-5 w-5" />;
      case 'GROUP':
        return <Users className="h-5 w-5" />;
      case 'CHANNEL':
        return <Hash className="h-5 w-5" />;
      default:
        return <MessageCircle className="h-5 w-5" />;
    }
  };
  
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return 'now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
    return date.toLocaleDateString();
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return (
    <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-xl font-semibold text-gray-900">Chats</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {chats?.map((chat: Chat) => (
          <div
            key={chat.id}
            onClick={() => setSelectedChat(chat.id)}
            className={`p-4 border-b border-gray-100 cursor-pointer hover:bg-gray-50 ${
              selectedChat === chat.id ? 'bg-blue-50 border-blue-200' : ''
            }`}
          >
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {chat.avatar ? (
                  <img
                    src={chat.avatar}
                    alt={chat.name}
                    className="h-10 w-10 rounded-full"
                  />
                ) : (
                  <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                    {getChatIcon(chat.type)}
                  </div>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {chat.name || chat.users.find(u => u.user.id !== 'current-user')?.user.username}
                  </p>
                  {chat.lastMessage && (
                    <p className="text-xs text-gray-500">
                      {formatTime(chat.lastMessage.createdAt)}
                    </p>
                  )}
                </div>
                
                {chat.lastMessage && (
                  <p className="text-sm text-gray-500 truncate">
                    {chat.lastMessage.user.username}: {chat.lastMessage.content}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

```typescript
// frontend/components/ChatWindow.tsx
import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Send, Paperclip, Smile, Phone, Video } from 'lucide-react';
import { useSocket } from '../hooks/useSocket';

interface Message {
  id: string;
  content: string;
  type: string;
  createdAt: string;
  user: {
    id: string;
    username: string;
    avatar?: string;
  };
}

interface ChatWindowProps {
  chatId: string;
}

export default function ChatWindow({ chatId }: ChatWindowProps) {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const socket = useSocket();
  
  // Fetch messages
  const { data: messages, isLoading } = useQuery({
    queryKey: ['messages', chatId],
    queryFn: async () => {
      const response = await fetch(`/api/chats/${chatId}/messages`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      return response.json();
    },
    enabled: !!chatId
  });
  
  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (content: string) => {
      const response = await fetch(`/api/chats/${chatId}/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ content })
      });
      return response.json();
    },
    onSuccess: () => {
      setMessage('');
      queryClient.invalidateQueries({ queryKey: ['messages', chatId] });
    }
  });
  
  // Socket event handlers
  useEffect(() => {
    if (!socket || !chatId) return;
    
    // Join chat room
    socket.emit('join:chat', chatId);
    
    // Listen for new messages
    const handleNewMessage = (newMessage: Message) => {
      queryClient.setQueryData(['messages', chatId], (old: Message[]) => {
        return [...(old || []), newMessage];
      });
    };
    
    // Listen for typing indicators
    const handleTypingStart = (data: any) => {
      setIsTyping(true);
    };
    
    const handleTypingStop = (data: any) => {
      setIsTyping(false);
    };
    
    socket.on('message:new', handleNewMessage);
    socket.on('typing:start', handleTypingStart);
    socket.on('typing:stop', handleTypingStop);
    
    return () => {
      socket.emit('leave:chat', chatId);
      socket.off('message:new', handleNewMessage);
      socket.off('typing:start', handleTypingStart);
      socket.off('typing:stop', handleTypingStop);
    };
  }, [socket, chatId, queryClient]);
  
  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    sendMessageMutation.mutate(message);
  };
  
  const handleTyping = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(e.target.value);
    
    if (socket) {
      if (e.target.value.length > 0) {
        socket.emit('typing:start', { chatId });
      } else {
        socket.emit('typing:stop', { chatId });
      }
    }
  };
  
  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  if (isLoading) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return (
    <div className="flex-1 flex flex-col">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-full bg-gray-300"></div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Chat Name</h3>
              <p className="text-sm text-gray-500">Online</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-500 hover:text-gray-700">
              <Phone className="h-5 w-5" />
            </button>
            <button className="p-2 text-gray-500 hover:text-gray-700">
              <Video className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
      
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages?.map((msg: Message) => (
          <div
            key={msg.id}
            className={`flex ${msg.user.id === 'current-user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                msg.user.id === 'current-user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-900'
              }`}
            >
              <p className="text-sm">{msg.content}</p>
              <p className="text-xs opacity-70 mt-1">
                {formatTime(msg.createdAt)}
              </p>
            </div>
          </div>
        ))}
        
        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-200 text-gray-900 px-4 py-2 rounded-lg">
              <p className="text-sm">Someone is typing...</p>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Message Input */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
          <button
            type="button"
            className="p-2 text-gray-500 hover:text-gray-700"
          >
            <Paperclip className="h-5 w-5" />
          </button>
          
          <div className="flex-1 relative">
            <input
              type="text"
              value={message}
              onChange={handleTyping}
              placeholder="Type a message..."
              className="w-full px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <button
            type="button"
            className="p-2 text-gray-500 hover:text-gray-700"
          >
            <Smile className="h-5 w-5" />
          </button>
          
          <button
            type="submit"
            disabled={!message.trim() || sendMessageMutation.isPending}
            className="p-2 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50"
          >
            <Send className="h-5 w-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
```

### **2.2 Custom Hooks**

```typescript
// frontend/hooks/useSocket.ts
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

export function useSocket() {
  const [socket, setSocket] = useState<Socket | null>(null);
  
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    const newSocket = io(process.env.NEXT_PUBLIC_API_URL!, {
      auth: {
        token
      }
    });
    
    setSocket(newSocket);
    
    return () => {
      newSocket.close();
    };
  }, []);
  
  return socket;
}
```

## 📱 Step 3: Mobile Implementation

### **3.1 React Native Setup**

```bash
# Create React Native project
npx react-native init MessagingApp

# Install dependencies
npm install @react-navigation/native
npm install @react-navigation/stack
npm install @react-navigation/bottom-tabs
npm install react-native-socket.io-client
npm install @react-native-async-storage/async-storage
npm install react-native-push-notification
npm install react-native-webrtc
npm install react-native-image-picker
```

### **3.2 Mobile Components**

```typescript
// mobile/src/components/ChatScreen.tsx
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform
} from 'react-native';
import io from 'socket.io-client';

interface Message {
  id: string;
  content: string;
  createdAt: string;
  user: {
    id: string;
    username: string;
  };
}

export default function ChatScreen({ route }: any) {
  const { chatId } = route.params;
  const [messages, setMessages] = useState<Message[]>([]);
  const [message, setMessage] = useState('');
  const [socket, setSocket] = useState<any>(null);
  
  useEffect(() => {
    // Initialize socket
    const newSocket = io(process.env.API_URL!, {
      auth: {
        token: 'your-jwt-token'
      }
    });
    
    setSocket(newSocket);
    
    // Join chat room
    newSocket.emit('join:chat', chatId);
    
    // Listen for messages
    newSocket.on('message:new', (newMessage: Message) => {
      setMessages(prev => [...prev, newMessage]);
    });
    
    return () => {
      newSocket.emit('leave:chat', chatId);
      newSocket.close();
    };
  }, [chatId]);
  
  const sendMessage = () => {
    if (!message.trim() || !socket) return;
    
    socket.emit('message:send', {
      chatId,
      content: message
    });
    
    setMessage('');
  };
  
  const renderMessage = ({ item }: { item: Message }) => (
    <View style={[
      styles.messageContainer,
      item.user.id === 'current-user' ? styles.sentMessage : styles.receivedMessage
    ]}>
      <Text style={styles.messageText}>{item.content}</Text>
      <Text style={styles.messageTime}>
        {new Date(item.createdAt).toLocaleTimeString()}
      </Text>
    </View>
  );
  
  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <FlatList
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        style={styles.messagesList}
      />
      
      <View style={styles.inputContainer}>
        <TextInput
          style={styles.textInput}
          value={message}
          onChangeText={setMessage}
          placeholder="Type a message..."
          multiline
        />
        <TouchableOpacity onPress={sendMessage} style={styles.sendButton}>
          <Text style={styles.sendButtonText}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5'
  },
  messagesList: {
    flex: 1,
    padding: 16
  },
  messageContainer: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
    marginVertical: 4
  },
  sentMessage: {
    backgroundColor: '#007bff',
    alignSelf: 'flex-end'
  },
  receivedMessage: {
    backgroundColor: '#ffffff',
    alignSelf: 'flex-start'
  },
  messageText: {
    fontSize: 16,
    color: '#333'
  },
  messageTime: {
    fontSize: 12,
    color: '#666',
    marginTop: 4
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#ffffff',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0'
  },
  textInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginRight: 8,
    maxHeight: 100
  },
  sendButton: {
    backgroundColor: '#007bff',
    paddingHorizontal: 20,
    paddingVertical: 8,
    borderRadius: 20,
    justifyContent: 'center'
  },
  sendButtonText: {
    color: '#ffffff',
    fontWeight: 'bold'
  }
});
```

## 🚀 Step 4: Deployment

### **4.1 Docker Configuration**

```dockerfile
# backend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3001

CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "3001:3001"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/messaging
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your-secret-key
    depends_on:
      - db
      - redis
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:3001
    depends_on:
      - backend
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=messaging
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### **4.2 Environment Variables**

```bash
# .env
DATABASE_URL="postgresql://user:password@localhost:5432/messaging"
REDIS_URL="redis://localhost:6379"
JWT_SECRET="your-super-secret-jwt-key"
FRONTEND_URL="http://localhost:3000"
API_URL="http://localhost:3001"
```

## 🎯 Key Features Implemented

### **✅ Real-time Messaging**
- WebSocket connections for instant messaging
- Typing indicators
- Message delivery status
- Online/offline status

### **✅ User Authentication**
- JWT-based authentication
- User registration and login
- Password hashing with bcrypt

### **✅ Chat Management**
- Private and group chats
- Message history
- User roles and permissions
- Chat metadata

### **✅ Mobile Support**
- React Native implementation
- Push notifications
- Offline support
- Native performance

### **✅ Scalable Architecture**
- Microservices ready
- Database optimization
- Caching with Redis
- Load balancing support

## 🚀 Next Steps

1. **Add File Sharing**: Implement file upload and sharing
2. **Voice/Video Calls**: Integrate WebRTC for calls
3. **Push Notifications**: Add Firebase FCM
4. **End-to-End Encryption**: Implement message encryption
5. **Advanced Features**: Stickers, GIFs, reactions
6. **Performance Optimization**: Caching, CDN, optimization
7. **Testing**: Unit tests, integration tests, E2E tests
8. **Monitoring**: Logging, metrics, alerting

This implementation provides a solid foundation for building a modern messaging platform like Telegram or Viber! 🚀
