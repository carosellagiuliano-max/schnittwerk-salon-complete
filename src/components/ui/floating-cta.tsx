import React from 'react';
import { MessageCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

const FloatingCTA = () => {
  const handleBooking = () => {
    window.open('tel:+41718019265', '_self');
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Button
        onClick={handleBooking}
        size="lg"
        className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-elegant rounded-full px-6 py-4 transition-elegant hover:scale-105"
      >
        <MessageCircle className="h-5 w-5 mr-2" />
        Jetzt Termin buchen
      </Button>
    </div>
  );
};

export default FloatingCTA;