# PrivyVote - Blockchain E-Voting System

A comprehensive secure electronic voting platform built with Django 5.2.6, featuring homomorphic encryption, modern UI/UX, and robust election management capabilities. Intikhab ensures transparency and privacy in democratic elections through advanced cryptographic techniques and professional-grade architecture.

## ✨ Key Features

### 🗳️ **Election Management**
- Create and manage public or private elections
- Flexible voting periods with start/end scheduling
- Real-time election status tracking (draft, active, closed)
- Comprehensive candidate management
- Election invitation system for private elections

### 🔐 **Security & Privacy**
- Paillier Homomorphic Encryption for vote privacy
- End-to-end encrypted voting process
- Secure vote verification without compromising privacy
- Protection against double voting
- UUID-based URL architecture for security

### 👥 **User Management**
- Multi-role authentication (Officials, Candidates, Citizens)
- Django Allauth integration for flexible authentication
- User profiles with role-based permissions
- Invitation-based access for private elections

### 🎨 **Modern Interface**
- Responsive Bootstrap 5.3.3 design
- Professional dashboard and admin interface
- Real-time vote counting and results display
- Accessible and mobile-friendly UI
- Clean, semantic HTML structure

### 📊 **Results & Verification**
- Transparent vote counting and percentage calculations
- Results verification using cryptographic proofs
- Detailed election statistics and analytics
- Export capabilities for election data

## 🛠️ Technology Stack

- **Backend**: Django 5.2.6 with Python 3.13
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Encryption**: Paillier Homomorphic Encryption (lightphe)
- **Frontend**: Bootstrap 5.3.3 + Bootstrap Icons 1.11.0
- **Authentication**: Django Allauth with social auth support
- **Testing**: pytest with comprehensive test coverage
- **Security**: CSRF protection, encrypted fields, secure sessions

## Prerequisites

- Python 3.x installed
- Basic understanding of command line operations
- pip (Python package manager)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ installed
- Git for version control
- Basic understanding of Django and command line operations

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/codeforpakistan/intikhab.git
cd intikhab
```

2. **Set up virtual environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment setup**
```bash
# Create .env file for environment variables
cp .env.example .env
# Edit .env with your configuration
```

5. **Database setup**
```bash
python manage.py migrate
python manage.py createsuperuser
```

6. **Seed sample data (optional)**
```bash
python manage.py seed
```

7. **Run development server**
```bash
python manage.py runserver
```

8. **Access the application**
- Main application: http://127.0.0.1:8000/
- Admin interface: http://127.0.0.1:8000/admin/

## 📁 Project Architecture

```
intikhab/
├── app/                          # Main Django application
│   ├── models/                   # Modular model architecture
│   │   ├── election.py          # Election model with crypto integration
│   │   ├── candidate.py         # Candidate management
│   │   ├── vote.py              # Encrypted vote storage
│   │   ├── invitation.py        # Election invitation system
│   │   ├── party.py             # Political party management
│   │   ├── profile.py           # Extended user profiles
│   │   └── user_extensions.py   # User permission extensions
│   ├── views/                    # Organized view modules
│   │   ├── election.py          # Election CRUD operations
│   │   ├── candidate.py         # Candidate management views
│   │   ├── vote.py              # Voting and results views
│   │   └── invitation.py        # Invitation handling
│   ├── templates/                # Modern Bootstrap templates
│   │   ├── app/
│   │   │   ├── elections/       # Election templates
│   │   │   ├── candidates/      # Candidate templates
│   │   │   ├── voting/          # Voting interface
│   │   │   ├── invitations/     # Invitation management
│   │   │   ├── partials/        # Reusable components
│   │   │   └── layouts/         # Base layouts
│   │   └── registration/        # Authentication templates
│   ├── static/app/              # Static assets
│   ├── management/commands/     # Custom Django commands
│   ├── signals/                 # Django signals for automation
│   ├── tests/                   # Comprehensive test suite
│   ├── admin.py                 # Enhanced admin interface
│   ├── encryption.py            # Homomorphic encryption utilities
│   └── forms.py                 # Django forms with validation
├── project/                     # Django project configuration
│   ├── settings.py              # Environment-based settings
│   ├── urls.py                  # Clean URL architecture
│   └── wsgi.py / asgi.py        # Production deployment
├── uploads/                     # Media file storage
├── .env.example                 # Environment configuration template
├── requirements.txt             # Python dependencies
└── manage.py                    # Django management script
```
## 🔐 How Homomorphic Encryption Works

Intikhab uses **Paillier Homomorphic Encryption** to achieve verifiable elections without compromising voter privacy:

### Encryption Process
1. **Key Generation**: Each election generates a unique public/private key pair
2. **Vote Encryption**: Individual votes are encrypted using the public key
3. **Homomorphic Addition**: Encrypted votes can be mathematically combined
4. **Result Decryption**: Only the final tally is decrypted, never individual votes

### Security Guarantees
- **Ballot Secrecy**: Individual votes remain encrypted and untraceable
- **Verifiable Results**: Mathematical proofs ensure accurate counting
- **Tamper Resistance**: Encrypted votes cannot be altered without detection
- **Zero-Knowledge Verification**: Results can be verified without revealing votes

### Technical Implementation
```python
# Simplified encryption flow
vote = candidate_selection
encrypted_vote = paillier_encrypt(vote, public_key)
vote_total = homomorphic_add(all_encrypted_votes)
final_result = paillier_decrypt(vote_total, private_key)
```

## 🛡️ Security Features

### Cryptographic Security
- **Paillier Homomorphic Encryption** for vote privacy
- **Secure random number generation** for cryptographic operations  
- **Public key infrastructure** for election integrity
- **Zero-knowledge proofs** for result verification

### Application Security
- **CSRF protection** on all forms and state-changing operations
- **UUID-based URLs** to prevent enumeration attacks
- **Role-based access control** with granular permissions
- **Session security** with secure cookie settings
- **Input validation** and sanitization across all user inputs

### Election Integrity
- **Double voting prevention** with unique constraints
- **Audit trails** for all election activities
- **Time-locked voting periods** with precise scheduling
- **Invitation-based access** for private elections
- **Result verification** through cryptographic proofs

## 📊 Election Management

### Election Types
- **Public Elections**: Open to all registered users
- **Private Elections**: Invitation-only with controlled access
- **Flexible Scheduling**: Custom start and end times
- **Real-time Status**: Draft, Active, Closed states

### Administrative Features
- **Candidate Management**: Add, edit, remove candidates
- **Invitation System**: Send and manage election invitations
- **Results Dashboard**: Real-time vote counting and analytics
- **User Management**: Role assignment and permission control

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python manage.py test

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test modules
python manage.py test app.tests.test_models
python manage.py test app.tests.test_views
python manage.py test app.tests.test_encryption
```

## 🚀 Deployment

### Production Settings
- Configure environment variables in `.env`
- Use PostgreSQL for production database
- Enable HTTPS and secure cookie settings
- Set up proper static file serving
- Configure email backend for notifications

### Docker Deployment
```bash
# Build and run with Docker
docker-compose up --build
```

## 🤝 Contributing

We welcome contributions to improve Intikhab! Here's how to get started:

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure all tests pass: `python manage.py test`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Code Standards
- Follow PEP 8 Python style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Use semantic commit messages
- Ensure Bootstrap components are used consistently

### Areas for Contribution
- 🔐 Enhanced encryption algorithms
- 🎨 UI/UX improvements
- 📱 Mobile responsiveness enhancements
- 🌐 Internationalization (i18n)
- 📊 Advanced analytics and reporting
- 🔄 API development for third-party integrations

## 📜 License

This project is open-sourced under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 📞 Contact & Support

- **Email**: [info@codeforpakistan.org](mailto:info@codeforpakistan.org)
- **Website**: [https://codeforpakistan.org](https://codeforpakistan.org)
- **GitHub Issues**: [Report bugs or request features](https://github.com/codeforpakistan/intikhab/issues)

---

## 📋 Recent Updates

### v2.0.0 - Major Architecture Improvements
- ✅ **URL Standardization**: Consistent UUID-based URL parameters across all endpoints
- ✅ **Modular Architecture**: Separated models, views, and templates into organized modules
- ✅ **Enhanced Security**: Improved CSRF protection and permission checking
- ✅ **Modern UI**: Updated to Bootstrap 5.3.3 with responsive design
- ✅ **Authentication**: Integrated Django Allauth for flexible user management
- ✅ **Testing**: Comprehensive test suite with pytest integration
- ✅ **Code Quality**: Professional Django patterns and best practices

### v1.0.0 - Initial Release
- 🗳️ Basic electronic voting functionality
- 🔐 Paillier homomorphic encryption implementation
- 👥 User authentication and role management
- 📊 Election results and verification system

---

<div align="center">

**Built with ❤️ by [Code for Pakistan](https://codeforpakistan.org)**

*Empowering democratic participation through secure technology*

</div>
