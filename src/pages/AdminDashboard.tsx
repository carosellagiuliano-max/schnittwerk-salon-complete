import React, { useState, useEffect } from 'react';
import { Calendar, Users, Package, Settings, Clock, Plus, Edit, Trash2, UserCheck, UserX, LogOut } from 'lucide-react';
import { apiService } from '@/services/api';
import { useAuth } from '@/contexts/auth-context';
import { Button } from '@/components/ui/button';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [appointments, setAppointments] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [services, setServices] = useState([]);
  const [products, setProducts] = useState([]);
  const [stylists, setStylists] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [showProductDialog, setShowProductDialog] = useState(false);
  const [showStylistDialog, setShowStylistDialog] = useState(false);
  const [showServiceDialog, setShowServiceDialog] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [editingStylist, setEditingStylist] = useState(null);
  const [editingService, setEditingService] = useState(null);

  const [productForm, setProductForm] = useState({
    name: '',
    description: '',
    detailed_description: '',
    usage: '',
    price: '',
    image: '',
    category: ''
  });

  const [stylistForm, setStylistForm] = useState({
    name: '',
    email: '',
    phone: '',
    specialties: ''
  });

  const [serviceForm, setServiceForm] = useState({
    name: '',
    category: '',
    service_type: '',
    duration: 60,
    price: 0,
    description: ''
  });

  const showToast = (message, type = 'success') => {
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 p-4 rounded-md text-white z-50 ${
      type === 'error' ? 'bg-red-500' : 'bg-green-500'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => document.body.removeChild(toast), 3000);
  };

  const loadData = async () => {
    try {
      const [appointmentsData, customersData, servicesData, productsData, stylistsData] = await Promise.all([
        apiService.getAdminAppointments(),
        apiService.getAdminCustomers(),
        apiService.getServices(),
        apiService.getProducts(),
        apiService.getStylists()
      ]);
      
      setAppointments(appointmentsData);
      setCustomers(customersData);
      setServices(servicesData);
      setProducts(productsData);
      setStylists(stylistsData);
    } catch (error) {
      showToast('Fehler beim Laden der Daten: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleProductSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingProduct) {
        await apiService.updateProduct(editingProduct.id, productForm);
        showToast('Produkt aktualisiert');
      } else {
        await apiService.createProduct(productForm);
        showToast('Produkt erstellt');
      }
      setShowProductDialog(false);
      setEditingProduct(null);
      setProductForm({
        name: '',
        description: '',
        detailed_description: '',
        usage: '',
        price: '',
        image: '',
        category: ''
      });
      loadData();
    } catch (error) {
      showToast('Fehler: ' + error.message, 'error');
    }
  };

  const handleStylistSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingStylist) {
        await apiService.updateStylist(editingStylist.id, stylistForm);
        showToast('Stylist aktualisiert');
      } else {
        await apiService.createStylist(stylistForm);
        showToast('Stylist erstellt');
      }
      setShowStylistDialog(false);
      setEditingStylist(null);
      setStylistForm({
        name: '',
        email: '',
        phone: '',
        specialties: ''
      });
      loadData();
    } catch (error) {
      showToast('Fehler: ' + error.message, 'error');
    }
  };

  const handleServiceSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingService) {
        await apiService.updateService(editingService.id, serviceForm);
        showToast('Service aktualisiert');
      } else {
        await apiService.createService(serviceForm);
        showToast('Service erstellt');
      }
      setShowServiceDialog(false);
      setEditingService(null);
      setServiceForm({
        name: '',
        category: '',
        service_type: '',
        duration: 60,
        price: 0,
        description: ''
      });
      loadData();
    } catch (error) {
      showToast('Fehler: ' + error.message, 'error');
    }
  };

  const handleDeleteProduct = async (productId) => {
    try {
      await apiService.deleteProduct(productId);
      showToast('Produkt gelöscht');
      loadData();
    } catch (error) {
      showToast('Fehler: ' + error.message, 'error');
    }
  };

  const handleDeleteStylist = async (stylistId) => {
    try {
      await apiService.deleteStylist(stylistId);
      showToast('Stylist gelöscht');
      loadData();
    } catch (error) {
      showToast('Fehler: ' + error.message, 'error');
    }
  };

  const handleBlockCustomer = async (customerId) => {
    try {
      await apiService.blockCustomer(customerId);
      showToast('Kunde gesperrt');
      loadData();
    } catch (error) {
      showToast('Fehler: ' + error.message, 'error');
    }
  };

  const handleUnblockCustomer = async (customerId) => {
    try {
      await apiService.unblockCustomer(customerId);
      showToast('Kunde entsperrt');
      loadData();
    } catch (error) {
      showToast('Fehler: ' + error.message, 'error');
    }
  };

  const handleCancelAppointment = async (appointmentId) => {
    try {
      await apiService.cancelAppointmentAdmin(appointmentId);
      showToast('Termin storniert');
      loadData();
    } catch (error) {
      showToast('Fehler: ' + error.message, 'error');
    }
  };

  const editProduct = (product) => {
    setEditingProduct(product);
    setProductForm({
      name: product.name,
      description: product.description || '',
      detailed_description: product.detailed_description || '',
      usage: product.usage || '',
      price: product.price,
      image: product.image,
      category: product.category
    });
    setShowProductDialog(true);
  };

  const editStylist = (stylist) => {
    setEditingStylist(stylist);
    setStylistForm({
      name: stylist.name,
      email: stylist.email || '',
      phone: stylist.phone || '',
      specialties: stylist.specialties || ''
    });
    setShowStylistDialog(true);
  };

  const editService = (service) => {
    setEditingService(service);
    setServiceForm({
      name: service.name,
      category: service.category,
      service_type: service.service_type,
      duration: service.duration,
      price: service.price,
      description: service.description || ''
    });
    setShowServiceDialog(true);
  };

  useEffect(() => {
    if (user?.is_admin) {
      loadData();
    }
  }, [user]);

  if (!user?.is_admin) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Zugriff verweigert</h1>
          <p className="text-gray-600">Sie haben keine Berechtigung für das Admin-Portal.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Lade Admin-Dashboard...</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Übersicht', icon: Settings },
    { id: 'appointments', label: 'Termine', icon: Calendar },
    { id: 'customers', label: 'Kunden', icon: Users },
    { id: 'services', label: 'Services', icon: Clock },
    { id: 'products', label: 'Produkte', icon: Package },
    { id: 'stylists', label: 'Stylisten', icon: Users }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600">Willkommen, {user.first_name}</p>
            </div>
            <Button
              onClick={logout}
              variant="outline"
              className="flex items-center space-x-2"
            >
              <LogOut className="h-4 w-4" />
              <span>Abmelden</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <Calendar className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Termine</p>
                  <p className="text-2xl font-bold text-gray-900">{appointments.length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <Users className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Kunden</p>
                  <p className="text-2xl font-bold text-gray-900">{customers.length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <Package className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Produkte</p>
                  <p className="text-2xl font-bold text-gray-900">{products.length}</p>
                </div>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="flex items-center">
                <Clock className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Services</p>
                  <p className="text-2xl font-bold text-gray-900">{services.length}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'appointments' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Terminverwaltung</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kunde</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Service</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Datum</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Zeit</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aktionen</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {appointments.map((apt) => (
                      <tr key={apt.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {apt.customer_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {apt.service_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(apt.appointment_date).toLocaleDateString('de-DE')}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {apt.appointment_time}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            apt.status === 'confirmed' ? 'bg-green-100 text-green-800' :
                            apt.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {apt.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <Button
                            onClick={() => handleCancelAppointment(apt.id)}
                            variant="outline"
                            size="sm"
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'customers' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">Kundenverwaltung</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">E-Mail</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Telefon</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aktionen</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {customers.map((customer) => (
                      <tr key={customer.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {customer.first_name} {customer.last_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {customer.email}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {customer.phone || 'N/A'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            customer.is_blocked ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {customer.is_blocked ? 'Gesperrt' : 'Aktiv'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          {customer.is_blocked ? (
                            <Button
                              onClick={() => handleUnblockCustomer(customer.id)}
                              variant="outline"
                              size="sm"
                              className="text-green-600 hover:text-green-900"
                            >
                              <UserCheck className="h-4 w-4" />
                            </Button>
                          ) : (
                            <Button
                              onClick={() => handleBlockCustomer(customer.id)}
                              variant="outline"
                              size="sm"
                              className="text-red-600 hover:text-red-900"
                            >
                              <UserX className="h-4 w-4" />
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'products' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Produktverwaltung</h3>
                <Button
                  onClick={() => setShowProductDialog(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Neues Produkt</span>
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                  <div key={product.id} className="border rounded-lg p-4">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-48 object-cover rounded-md mb-4"
                    />
                    <h4 className="font-semibold text-lg mb-2">{product.name}</h4>
                    <p className="text-gray-600 text-sm mb-2">{product.description}</p>
                    <p className="text-lg font-bold text-green-600 mb-4">{product.price}</p>
                    <div className="flex space-x-2">
                      <Button
                        onClick={() => editProduct(product)}
                        variant="outline"
                        size="sm"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        onClick={() => handleDeleteProduct(product.id)}
                        variant="outline"
                        size="sm"
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'services' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Service-Verwaltung</h3>
                <Button
                  onClick={() => setShowServiceDialog(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Neuer Service</span>
                </Button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kategorie</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Typ</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dauer</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Preis</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Aktionen</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {services.map((service) => (
                      <tr key={service.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {service.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {service.category}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {service.service_type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {service.duration} min
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          CHF {service.price}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                          <Button
                            onClick={() => editService(service)}
                            variant="outline"
                            size="sm"
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'stylists' && (
          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Stylisten-Verwaltung</h3>
                <Button
                  onClick={() => setShowStylistDialog(true)}
                  className="flex items-center space-x-2"
                >
                  <Plus className="h-4 w-4" />
                  <span>Neuer Stylist</span>
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {stylists.map((stylist) => (
                  <div key={stylist.id} className="border rounded-lg p-4">
                    <h4 className="font-semibold text-lg mb-2">{stylist.name}</h4>
                    <p className="text-gray-600 text-sm mb-2">{stylist.email}</p>
                    <p className="text-gray-600 text-sm mb-2">{stylist.phone}</p>
                    <p className="text-gray-600 text-sm mb-4">{stylist.specialties}</p>
                    <div className="flex space-x-2">
                      <Button
                        onClick={() => editStylist(stylist)}
                        variant="outline"
                        size="sm"
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button
                        onClick={() => handleDeleteStylist(stylist.id)}
                        variant="outline"
                        size="sm"
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Product Dialog */}
      {showProductDialog && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingProduct ? 'Produkt bearbeiten' : 'Neues Produkt'}
              </h3>
              <form onSubmit={handleProductSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    value={productForm.name}
                    onChange={(e) => setProductForm({...productForm, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Beschreibung</label>
                  <textarea
                    value={productForm.description}
                    onChange={(e) => setProductForm({...productForm, description: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Preis</label>
                  <input
                    type="text"
                    value={productForm.price}
                    onChange={(e) => setProductForm({...productForm, price: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Bild URL</label>
                  <input
                    type="url"
                    value={productForm.image}
                    onChange={(e) => setProductForm({...productForm, image: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Kategorie</label>
                  <input
                    type="text"
                    value={productForm.category}
                    onChange={(e) => setProductForm({...productForm, category: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowProductDialog(false);
                      setEditingProduct(null);
                    }}
                  >
                    Abbrechen
                  </Button>
                  <Button type="submit">
                    {editingProduct ? 'Aktualisieren' : 'Erstellen'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Stylist Dialog */}
      {showStylistDialog && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingStylist ? 'Stylist bearbeiten' : 'Neuer Stylist'}
              </h3>
              <form onSubmit={handleStylistSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    value={stylistForm.name}
                    onChange={(e) => setStylistForm({...stylistForm, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">E-Mail</label>
                  <input
                    type="email"
                    value={stylistForm.email}
                    onChange={(e) => setStylistForm({...stylistForm, email: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Telefon</label>
                  <input
                    type="tel"
                    value={stylistForm.phone}
                    onChange={(e) => setStylistForm({...stylistForm, phone: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Spezialisierungen</label>
                  <textarea
                    value={stylistForm.specialties}
                    onChange={(e) => setStylistForm({...stylistForm, specialties: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows={3}
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowStylistDialog(false);
                      setEditingStylist(null);
                    }}
                  >
                    Abbrechen
                  </Button>
                  <Button type="submit">
                    {editingStylist ? 'Aktualisieren' : 'Erstellen'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Service Dialog */}
      {showServiceDialog && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {editingService ? 'Service bearbeiten' : 'Neuer Service'}
              </h3>
              <form onSubmit={handleServiceSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <input
                    type="text"
                    value={serviceForm.name}
                    onChange={(e) => setServiceForm({...serviceForm, name: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Kategorie</label>
                  <select
                    value={serviceForm.category}
                    onChange={(e) => setServiceForm({...serviceForm, category: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  >
                    <option value="">Wählen Sie eine Kategorie</option>
                    <option value="haircut">Haarschnitt</option>
                    <option value="coloring">Färbung</option>
                    <option value="styling">Styling</option>
                    <option value="treatment">Behandlung</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Service-Typ</label>
                  <select
                    value={serviceForm.service_type}
                    onChange={(e) => setServiceForm({...serviceForm, service_type: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  >
                    <option value="">Wählen Sie einen Typ</option>
                    <option value="women">Damen</option>
                    <option value="men">Herren</option>
                    <option value="both">Beide</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Dauer (Minuten)</label>
                  <input
                    type="number"
                    value={serviceForm.duration}
                    onChange={(e) => setServiceForm({...serviceForm, duration: parseInt(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Preis (CHF)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={serviceForm.price}
                    onChange={(e) => setServiceForm({...serviceForm, price: parseFloat(e.target.value)})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Beschreibung</label>
                  <textarea
                    value={serviceForm.description}
                    onChange={(e) => setServiceForm({...serviceForm, description: e.target.value})}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                    rows={3}
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setShowServiceDialog(false);
                      setEditingService(null);
                    }}
                  >
                    Abbrechen
                  </Button>
                  <Button type="submit">
                    {editingService ? 'Aktualisieren' : 'Erstellen'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
