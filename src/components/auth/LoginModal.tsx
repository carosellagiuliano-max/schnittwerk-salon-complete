import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Mail, Lock, Eye, EyeOff, ArrowLeft, Users, Shield } from 'lucide-react';
import { useAuth } from '@/contexts/auth-context';
import { toast } from '@/hooks/use-toast';

interface LoginModalProps {
  children: React.ReactNode;
}

type PortalType = 'admin' | 'customer' | null;

const LoginModal = ({ children }: LoginModalProps) => {
  const { login, register, isAuthenticated, user } = useAuth();
  const [selectedPortal, setSelectedPortal] = useState<PortalType>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phone, setPhone] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [open, setOpen] = useState(false);

  const handlePortalSelect = (portal: PortalType) => {
    setSelectedPortal(portal);
    setIsRegistering(false);
    setEmail('');
    setPassword('');
    setFirstName('');
    setLastName('');
    setPhone('');
    setShowPassword(false);
  };

  const handleBack = () => {
    if (isRegistering) {
      setIsRegistering(false);
      setFirstName('');
      setLastName('');
      setPhone('');
    } else {
      setSelectedPortal(null);
    }
    setEmail('');
    setPassword('');
    setShowPassword(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (isRegistering) {
        if (selectedPortal !== 'customer') {
          throw new Error('Registration is only available for customers');
        }
        
        await register({
          email,
          password,
          first_name: firstName,
          last_name: lastName,
          phone: phone || undefined
        });

        toast({
          title: 'Registrierung erfolgreich!',
          description: 'Ihr Konto wurde erstellt und Sie sind jetzt angemeldet.'
        });
      } else {
        await login({ email, password });

        if (selectedPortal === 'admin' && user && !user.is_admin) {
          throw new Error('Sie haben keine Administratorrechte');
        }

        toast({
          title: 'Anmeldung erfolgreich!',
          description: `Willkommen ${selectedPortal === 'admin' ? 'im Adminportal' : 'zurück'}!`
        });
      }

      setOpen(false);
      handleBack();
      
      if (selectedPortal === 'admin' && user?.is_admin) {
        window.location.href = '/admin';
      }
      
      if (selectedPortal === 'admin' && user?.is_admin) {
        window.location.href = '/admin';
      }
    } catch (error: any) {
      toast({
        title: isRegistering ? 'Registrierung fehlgeschlagen' : 'Anmeldung fehlgeschlagen',
        description: error.message || 'Bitte überprüfen Sie Ihre Eingaben.',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getPortalTitle = () => {
    if (isRegistering) {
      return 'Konto erstellen';
    }
    switch (selectedPortal) {
      case 'admin':
        return 'Adminportal Login';
      case 'customer':
        return 'Kundenportal Login';
      default:
        return 'Portal auswählen';
    }
  };

  const getPortalPlaceholder = () => {
    switch (selectedPortal) {
      case 'admin':
        return 'admin@schnittwerk.com';
      case 'customer':
        return 'ihre.email@example.com';
      default:
        return '';
    }
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-[400px]">
        <DialogHeader>
          <DialogTitle className="text-2xl font-heading text-primary text-center">
            {getPortalTitle()}
          </DialogTitle>
        </DialogHeader>

        {/* Portal Selection Step */}
        {!selectedPortal && (
          <div className="space-y-4">
            <p className="text-center text-muted-foreground mb-6">
              Bitte wählen Sie Ihren Zugangsbereich:
            </p>
            
            <div className="space-y-3">
              <Button
                variant="outline"
                className="portal-selection-card w-full h-16 flex items-center justify-start space-x-4 text-left"
                onClick={() => handlePortalSelect('admin')}
              >
                <div className="bg-primary/10 p-3 rounded-lg">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <div className="font-semibold text-foreground">Adminportal</div>
                  <div className="text-sm text-muted-foreground">
                    Für Mitarbeiter und Administratoren
                  </div>
                </div>
              </Button>

              <Button
                variant="outline"
                className="portal-selection-card w-full h-16 flex items-center justify-start space-x-4 text-left"
                onClick={() => handlePortalSelect('customer')}
              >
                <div className="bg-primary/10 p-3 rounded-lg">
                  <Users className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <div className="font-semibold text-foreground">Kundenportal</div>
                  <div className="text-sm text-muted-foreground">
                    Für Kunden und Terminbuchungen
                  </div>
                </div>
              </Button>
            </div>
          </div>
        )}

        {/* Login Form Step */}
        {selectedPortal && (
          <>
            <Button
              variant="ghost"
              size="sm"
              className="w-fit mb-2"
              onClick={handleBack}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Zurück zur Auswahl
            </Button>

            <form onSubmit={handleSubmit} className="space-y-4">
              {isRegistering && (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="firstName" className="text-sm font-medium">
                        Vorname
                      </Label>
                      <Input
                        id="firstName"
                        type="text"
                        placeholder="Max"
                        value={firstName}
                        onChange={(e) => setFirstName(e.target.value)}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="lastName" className="text-sm font-medium">
                        Nachname
                      </Label>
                      <Input
                        id="lastName"
                        type="text"
                        placeholder="Mustermann"
                        value={lastName}
                        onChange={(e) => setLastName(e.target.value)}
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone" className="text-sm font-medium">
                      Telefon (optional)
                    </Label>
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="+41 71 123 45 67"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                    />
                  </div>
                </>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">
                  E-Mail
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder={getPortalPlaceholder()}
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="login-form-input pl-10"
                    required
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">
                  Passwort
                </Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Ihr Passwort"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="login-form-input pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-muted-foreground hover:text-foreground transition-elegant"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {!isRegistering && (
                <div className="flex items-center justify-between text-sm">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input type="checkbox" className="rounded border-border" />
                    <span className="text-muted-foreground">Angemeldet bleiben</span>
                  </label>
                  <button
                    type="button"
                    className="text-primary hover:underline transition-elegant"
                  >
                    Passwort vergessen?
                  </button>
                </div>
              )}

              <Button 
                type="submit" 
                className="w-full bg-primary hover:bg-primary/90 transition-elegant"
                disabled={isLoading}
              >
                {isLoading ? 'Wird verarbeitet...' : (
                  isRegistering ? 'Konto erstellen' : 
                  selectedPortal === 'admin' ? 'Admin Anmeldung' : 'Anmelden'
                )}
              </Button>

              {selectedPortal === 'customer' && (
                <div className="text-center text-sm text-muted-foreground">
                  {isRegistering ? (
                    <>
                      Bereits ein Konto?{' '}
                      <button
                        type="button"
                        className="text-primary hover:underline transition-elegant"
                        onClick={() => setIsRegistering(false)}
                      >
                        Anmelden
                      </button>
                    </>
                  ) : (
                    <>
                      Noch kein Konto?{' '}
                      <button
                        type="button"
                        className="text-primary hover:underline transition-elegant"
                        onClick={() => setIsRegistering(true)}
                      >
                        Registrieren
                      </button>
                    </>
                  )}
                </div>
              )}
            </form>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default LoginModal;
