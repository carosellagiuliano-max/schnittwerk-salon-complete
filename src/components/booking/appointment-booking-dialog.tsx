import React, { useState, useEffect } from 'react'
import { format } from 'date-fns'
import { de } from 'date-fns/locale'
import { CalendarIcon, Clock, Scissors, Users } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Calendar } from '@/components/ui/calendar'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog'
import {
  Popover,
  PopoverContent,
  PopoverTrigger
} from '@/components/ui/popover'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { toast } from '@/hooks/use-toast'
import { useAuth } from '@/contexts/auth-context'
import { apiService, Service, AvailabilitySlot } from '@/services/api'
import HaircutLengthDialog from './haircut-length-dialog'
import AdditionalServicesDialog from './additional-services-dialog'

// Using existing team owner image for Vanessa
import vanessaLogo from '@/assets/team-owner.jpg'

interface AppointmentBookingDialogProps {
  children: React.ReactNode
}

const hairdressers = [
  {
    id: 1,
    name: 'Maria Schmidt',
    specialty: 'Damenschnitte, Färben',
    image: vanessaLogo,
    description: 'Erfahrene Friseurin mit über 10 Jahren Berufserfahrung. Spezialisiert auf moderne Schnitte und Farbbehandlungen.'
  },
  {
    id: 2,
    name: 'Thomas Müller',
    specialty: 'Herrenschnitte, Bartpflege',
    image: vanessaLogo,
    description: 'Spezialist für Herrenschnitte und moderne Bartpflege.'
  }
]

export function AppointmentBookingDialog({
  children
}: AppointmentBookingDialogProps) {
  const { user, isAuthenticated } = useAuth()
  const [open, setOpen] = useState(false)
  const [step, setStep] = useState<'gender' | 'haircut' | 'booking' | 'additional'>('gender')
  const [selectedGender, setSelectedGender] = useState<'women' | 'men' | null>(null)
  const [selectedHaircut, setSelectedHaircut] = useState<any>(null)
  const [selectedDate, setSelectedDate] = useState<Date>()
  const [selectedTime, setSelectedTime] = useState<string>()
  const [selectedHairdresser, setSelectedHairdresser] = useState<number>()
  const [selectedService, setSelectedService] = useState<Service | null>(null)
  const [calendarOpen, setCalendarOpen] = useState(false)
  const [showHaircutDialog, setShowHaircutDialog] = useState(false)
  const [showAdditionalDialog, setShowAdditionalDialog] = useState(false)
  const [selectedAdditionalServices, setSelectedAdditionalServices] = useState<any[]>([])
  const [services, setServices] = useState<Service[]>([])
  const [availableSlots, setAvailableSlots] = useState<AvailabilitySlot[]>([])
  const [isLoadingAvailability, setIsLoadingAvailability] = useState(false)

  const handleDateSelect = async (date: Date | undefined) => {
    setSelectedDate(date)
    if (date) {
      setCalendarOpen(false)
      setSelectedTime(undefined)
      if (selectedService) {
        await loadAvailability(date, selectedService.id)
      }
    }
  }

  const loadAvailability = async (date: Date, serviceId: number) => {
    setIsLoadingAvailability(true)
    try {
      const dateStr = format(date, 'yyyy-MM-dd')
      const slots = await apiService.getAvailability(dateStr, serviceId)
      setAvailableSlots(slots)
    } catch (error) {
      toast({
        title: 'Fehler beim Laden der Verfügbarkeit',
        description: 'Bitte versuchen Sie es später erneut.',
        variant: 'destructive'
      })
    } finally {
      setIsLoadingAvailability(false)
    }
  }

  useEffect(() => {
    const loadServices = async () => {
      try {
        const allServices = await apiService.getServices()
        setServices(allServices)
      } catch (error) {
        toast({
          title: 'Fehler beim Laden der Services',
          description: 'Bitte versuchen Sie es später erneut.',
          variant: 'destructive'
        })
      }
    }

    if (open) {
      loadServices()
    }
  }, [open])

  const handleGenderSelect = (gender: 'women' | 'men') => {
    setSelectedGender(gender)
    setStep('haircut')
    setShowHaircutDialog(true)
  }

  const handleHaircutSelect = async (haircutId: string, haircutData: any) => {
    setSelectedHaircut(haircutData)
    setShowHaircutDialog(false)
    setStep('booking')
    
    const service = services.find(s => 
      s.category === selectedGender && 
      s.service_type === 'haircut' &&
      s.name.toLowerCase().includes(haircutData.name.toLowerCase().includes('kurz') ? 'kurz' : 'lang')
    )
    
    if (service) {
      setSelectedService(service)
      if (selectedDate) {
        await loadAvailability(selectedDate, service.id)
      }
    }
  }

  const handleBookingRequest = () => {
    if (!isAuthenticated) {
      toast({
        title: 'Anmeldung erforderlich',
        description: 'Bitte melden Sie sich an, um einen Termin zu buchen.',
        variant: 'destructive'
      })
      return
    }

    if (
      !selectedDate ||
      !selectedTime ||
      !selectedHairdresser ||
      !selectedService
    ) {
      toast({
        title: 'Bitte alle Felder ausfüllen',
        description: 'Datum, Zeit, Friseur und Behandlung müssen ausgewählt werden.',
        variant: 'destructive'
      })
      return
    }

    setStep('additional')
    setShowAdditionalDialog(true)
  }

  const handleAdditionalServicesConfirm = async (additionalServices: any[]) => {
    setSelectedAdditionalServices(additionalServices)
    setShowAdditionalDialog(false)
    
    if (!selectedDate || !selectedTime || !selectedHairdresser || !selectedService) {
      return
    }

    try {
      const appointmentDateTime = new Date(selectedDate)
      const [hours, minutes] = selectedTime.split(':').map(Number)
      appointmentDateTime.setHours(hours, minutes, 0, 0)

      const additionalServiceIds = additionalServices
        .map(service => services.find(s => s.name === service.name)?.id)
        .filter(Boolean) as number[]

      await apiService.createAppointment({
        stylist_id: selectedHairdresser,
        service_id: selectedService.id,
        appointment_date: appointmentDateTime.toISOString(),
        additional_services: additionalServiceIds.length > 0 ? additionalServiceIds : undefined,
        notes: undefined
      })

      const hairdresser = hairdressers.find(h => h.id === selectedHairdresser)
      
      toast({
        title: 'Termin erfolgreich gebucht!',
        description: `Ihr Termin am ${format(selectedDate, 'dd.MM.yyyy')} um ${selectedTime} bei ${hairdresser?.name} wurde gebucht.`
      })

      // Reset all states
      resetBooking()
      setOpen(false)
    } catch (error) {
      toast({
        title: 'Fehler beim Buchen',
        description: 'Der Termin konnte nicht gebucht werden. Bitte versuchen Sie es erneut.',
        variant: 'destructive'
      })
    }
  }

  const resetBooking = () => {
    setStep('gender')
    setSelectedGender(null)
    setSelectedHaircut(null)
    setSelectedDate(undefined)
    setSelectedTime(undefined)
    setSelectedHairdresser(undefined)
    setSelectedService(null)
    setSelectedAdditionalServices([])
    setAvailableSlots([])
  }

  return (
    <>
      <Dialog open={open} onOpenChange={(isOpen) => {
        setOpen(isOpen)
        if (!isOpen) resetBooking()
      }}>
        <DialogTrigger asChild>{children}</DialogTrigger>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Termin buchen</DialogTitle>
            <DialogDescription>
              {step === 'gender' && 'Wählen Sie zuerst die Art des Haarschnitts'}
              {step === 'haircut' && 'Wählen Sie Ihren gewünschten Haarschnitt'}
              {step === 'booking' && 'Wählen Sie Datum, Zeit und Friseur'}
              {step === 'additional' && 'Zusätzliche Leistungen auswählen'}
            </DialogDescription>
          </DialogHeader>

          {step === 'gender' && (
            <div className="space-y-4 py-6">
              <div className="text-center mb-6">
                <h3 className="text-lg font-semibold mb-2">Für wen ist der Termin?</h3>
                <p className="text-sm text-muted-foreground">Wählen Sie die passende Kategorie</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <Card 
                  className="cursor-pointer hover:shadow-soft transition-elegant border-2 hover:border-primary"
                  onClick={() => handleGenderSelect('women')}
                >
                  <CardContent className="p-6 text-center">
                    <div className="mb-4">
                      <div className="mx-auto w-16 h-16 bg-pink-100 rounded-full flex items-center justify-center">
                        <Scissors className="h-8 w-8 text-pink-600" />
                      </div>
                    </div>
                    <CardTitle className="text-lg">Damenschnitt</CardTitle>
                    <CardDescription className="mt-2">
                      Individueller Schnitt mit Haarlängen-Auswahl
                    </CardDescription>
                  </CardContent>
                </Card>

                <Card 
                  className="cursor-pointer hover:shadow-soft transition-elegant border-2 hover:border-primary"
                  onClick={() => handleGenderSelect('men')}
                >
                  <CardContent className="p-6 text-center">
                    <div className="mb-4">
                      <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                        <Users className="h-8 w-8 text-blue-600" />
                      </div>
                    </div>
                    <CardTitle className="text-lg">Herrenschnitt</CardTitle>
                    <CardDescription className="mt-2">
                      Klassische und moderne Herrenfrisuren
                    </CardDescription>
                  </CardContent>
                </Card>
              </div>
            </div>
          )}

          {step === 'booking' && selectedHaircut && (
            <div className="space-y-6 py-2">
              {/* Selected Service Display */}
              {selectedService && (
                <div className="p-3 bg-primary/5 rounded-lg border border-primary/20">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-medium">{selectedService.name}</h4>
                      <p className="text-sm text-muted-foreground">{selectedService.description}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">ab CHF {selectedService.price_from}</p>
                      <p className="text-xs text-muted-foreground">{selectedService.duration_minutes} min</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Datum */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Datum</label>
                <Popover open={calendarOpen} onOpenChange={setCalendarOpen}>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className={cn(
                        'w-full justify-start text-left font-normal',
                        !selectedDate && 'text-muted-foreground'
                      )}
                      onClick={() => setCalendarOpen(true)}
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {selectedDate
                        ? format(selectedDate, 'dd.MM.yyyy', { locale: de })
                        : 'Datum wählen'}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      selected={selectedDate}
                      onSelect={handleDateSelect}
                      disabled={date => date < new Date() || date.getDay() === 0}
                      initialFocus
                      className="p-3 pointer-events-auto"
                      locale={de}
                    />
                  </PopoverContent>
                </Popover>
              </div>

              {/* Uhrzeit */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Uhrzeit</label>
                <Select value={selectedTime} onValueChange={setSelectedTime} disabled={!selectedDate || isLoadingAvailability}>
                  <SelectTrigger>
                    <Clock className="mr-2 h-4 w-4" />
                    <SelectValue placeholder={isLoadingAvailability ? "Lade Verfügbarkeit..." : "Zeit wählen"} />
                  </SelectTrigger>
                  <SelectContent>
                    {availableSlots
                      .filter(slot => slot.available)
                      .map(slot => (
                        <SelectItem key={`${slot.stylist_id}-${slot.time}`} value={slot.time}>
                          {slot.time} - {slot.stylist_name}
                        </SelectItem>
                      ))}
                    {availableSlots.filter(slot => slot.available).length === 0 && selectedDate && !isLoadingAvailability && (
                      <SelectItem value="" disabled>
                        Keine verfügbaren Zeiten
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>

              {/* Friseur/Stylist - Auto-selected based on time slot */}
              {selectedTime && (
                <div className="space-y-2">
                  <label className="text-sm font-medium">Friseur/Stylist</label>
                  <div className="p-3 bg-muted rounded-lg">
                    {(() => {
                      const selectedSlot = availableSlots.find(slot => slot.time === selectedTime && slot.available)
                      if (selectedSlot) {
                        if (selectedHairdresser !== selectedSlot.stylist_id) {
                          setSelectedHairdresser(selectedSlot.stylist_id)
                        }
                        const stylist = hairdressers.find(h => h.id === selectedSlot.stylist_id)
                        return (
                          <div className="flex items-center gap-2">
                            <img
                              src={stylist?.image || vanessaLogo}
                              alt={selectedSlot.stylist_name}
                              className="w-8 h-8 rounded-full object-cover"
                            />
                            <div>
                              <p className="font-medium">{selectedSlot.stylist_name}</p>
                              <p className="text-sm text-muted-foreground">{stylist?.specialty}</p>
                            </div>
                          </div>
                        )
                      }
                      return <p className="text-muted-foreground">Bitte wählen Sie zuerst eine Zeit</p>
                    })()}
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <Button variant="outline" onClick={resetBooking} className="flex-1">
                  Zurück
                </Button>
                <Button
                  className="flex-1"
                  disabled={
                    !selectedDate ||
                    !selectedTime ||
                    !selectedHairdresser
                  }
                  onClick={handleBookingRequest}
                >
                  Termin buchen
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <HaircutLengthDialog
        isOpen={showHaircutDialog}
        onClose={() => setShowHaircutDialog(false)}
        onSelect={handleHaircutSelect}
        genderType={selectedGender || 'women'}
      />

      <AdditionalServicesDialog
        isOpen={showAdditionalDialog}
        onClose={() => setShowAdditionalDialog(false)}
        onConfirm={handleAdditionalServicesConfirm}
        genderType={selectedGender || 'women'}
      />
    </>
  )
}
