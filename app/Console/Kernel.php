protected function schedule(Schedule $schedule)
{
    $schedule->command('your:command')
             ->daily();
    
    // Or for more specific timing:
    $schedule->command('your:command')
             ->hourly()
             // ->weekly()
             // ->monthlyOn(1, '15:00');
} 