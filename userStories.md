**User Stories For Epics**


**Interactive Map**

**Story 1**

As a user, I want to view an interactive map of NYC when I open the app, so that I have a visual starting point for my trip.

* Given I have opened the app, when the map screen loads, then I see a map of NYC with readable streets and labels.
* Given the map is displayed, when I move the map or change its zoom level, then the view updates to the area and level of detail I chose.
* Given I am using a phone of any supported size or orientation, when the map is displayed, then the map and its controls fit the screen and remain usable.
* Given the map is loading or cannot load, when the map data is delayed or unavailable, then I am told it is loading or shown a message explaining the problem, and I can try again.

**Story 2**

As a user, I want to see my current location on the map, so that I know where I am relative to the route and stops.

* Given I have not shared my location, when I choose to show it, then I am asked for permission to use my location.
* Given I have granted permission, when I view the map, then my location is shown and stays current as I move.
* Given I have denied permission or my location is unavailable, when I view the map, then I can still use the map, and I am told why my location is not shown and how to enable it.
* Given I have moved the map away from my location, when I ask to return to my location, then the map shows where I am.

**Story 3**

As a user, I want to see my planned route on the map, so that I can visualize the whole trip.

* Given I have a planned trip, when I view the route on the map, then I see the path from my starting point to my destination, with both clearly marked.
* Given my route uses more than one mode of travel, when I view the route, then each part is distinguishable by mode and labeled with its line name or number.
* Given I am viewing a route, when I select part of it, then I see the mode and details for that part.
* Given I am viewing a route, when I look for what the symbols mean, then I can find an explanation of the route and marker types.
* Given I am viewing the map, when route and marker information is shown, then it is readable and does not depend on color alone to convey meaning.

**Story 4**

As a rider on a trip, I want to see my position along the route, so that I can tell how far I have come and how far is left.

* Given I am traveling on a planned route with location enabled, when my position changes, then I can tell which part of the route I have completed and which part remains.
* Given I am traveling on a planned route, when I view the map, then I can see my upcoming stops.
* Given I have the app open during a trip, when I move, then my position on the route updates without my having to refresh.

**Story 5**

As a user, I want to see my entire route at once, so that I can understand the big picture without adjusting the map manually.

* Given I have a planned route, when it is first displayed, then the whole route is visible on the screen.
* Given I have moved or zoomed away from my route, when I ask to see the full route again, then the whole route is visible again.
* Given the map is shown alongside other information, when I choose to enlarge the map, then it fills the screen.


**Real-Time Transit Updates**

**Story 1**

As a rider, I want to see real-time arrival times alongside the scheduled times for a line or stop, so that I know when my bus or train will actually arrive.

- Given I am viewing a line or stop, when arrivals are displayed, then I see each arrival's scheduled time, estimated live time, and minutes until arrival, along with its line, direction, and destination.
- Given I am viewing arrivals, when new live information becomes available, then the times update without my having to refresh.
- Given live information is not available for a trip, when I view its arrival, then I see the scheduled time and am told it is scheduled rather than live.

**Story 2**

As a rider, I want to see whether a bus or train is on time, delayed, or canceled, so that I can adjust my plans before I am waiting at the stop.

- Given I am viewing a trip, when I check its status, then I can tell whether it is on time, delayed (and by how many minutes), or canceled.
- Given a trip has been canceled, when I view upcoming arrivals, then the canceled trip is clearly identified as canceled and is not listed as an upcoming arrival.
- Given I am viewing a trip, when its status changes, then I see the updated status without refreshing.
- Given a status is shown, when I read it, then its meaning does not depend on color alone.

**Story 3**

As a rider, I want to see service changes such as reroutes, skipped stops, and planned work, so that I can plan around them.

- Given there are active service changes, when I open the service alerts, then I see a list of them that I can narrow down by line.
- Given I am reading an alert, when I view its details, then I see what changed, which lines and stops are affected, and when it applies.
- Given a service change affects a line or stop I am viewing, when the screen is displayed, then I see that alert there.
- Given there is planned future work, when I view alerts, then it is separated from current disruptions.

**Story 4**

As a commuter, I want to be notified about delays, cancellations, and service changes on the lines I use, so that I find out even when I am not using the app.

- Given I have chosen lines or saved routes to follow, when a delay, cancellation, or service change affects them, then I am notified even if the app is closed.
- Given I have not allowed notifications, when I use the app, then every other feature still works.
- Given I have chosen which types of notifications I want and my quiet hours, when an update occurs, then I receive only the types I chose and none during quiet hours.
- Given I receive a notification, when I open it, then I am taken to the relevant alert or line.

**Story 5**

As a rider, I want to know how recent the information is, so that I can trust it when making decisions.

- Given I am viewing live information, when it is displayed, then I can see when it was last updated.
- Given the information is out of date or the live source is unavailable, when I view it, then I am warned.
- Given my device is offline, when I view previously loaded information, then I see the last known information and am told it is out of date.
- Given an error occurs while loading information, when it happens, then I am shown a message and can try again.


**Trip Planner**

**Story 1**

As a user, I want to enter where I am starting and where I am going, so that the app can plan my trip.

- Given I am planning a trip, when I enter an origin or destination as an address, landmark, or place name, then I am offered matching suggestions as I type.
- Given I am entering an origin, when I choose to use my current location, then my current location is set as the starting point.
- Given I have entered an origin and destination, when I ask to reverse them, then they swap.
- Given I enter a place that cannot be found, when I submit it, then I am told and asked to try again.

**Story 2**

As a user, I want to choose a date and time up to a month ahead, so that I can plan outings that are not happening today.

- Given I am planning a trip, when I choose a departure or arrival time, then the results are based on that time.
- Given I choose a date in the past or more than 30 days ahead, when I try to plan, then I am told about the limit and cannot plan for that date.
- Given I have not chosen a time, when I plan a trip, then it is planned for leaving now, and the time used is visible on the results.
- Given I plan a trip for a future date, when the results are displayed, then they are based on scheduled service for that date, including known planned service changes, and are labeled as scheduled rather than live.

**Story 3**

As a user, I want to see several route options for my trip, so that I can choose the one that suits me.

- Given I have entered a trip, when results are displayed, then each option shows total time, departure and arrival times, transfers, walking time, and fare.
- Given results are displayed, when routes are possible with several modes, then options combine subway, bus, walking, and bike where appropriate.
- Given results are displayed, when I choose to sort or filter by fastest, fewest transfers, or least walking, then the options are reordered or narrowed accordingly.
- Given I select an option, when it opens, then I see step-by-step directions and can view the route on the map.

**Story 4**

As a user, I want to save a future trip, so that I can secure my plans and find them again before the outing.

- Given I have planned a trip, when I choose to save it, then its route, date, and time are stored.
- Given I have saved trips, when I open my upcoming trips, then they are listed in date order.
- Given I have a saved trip, when I edit its date or time, re-run the plan, or delete it, then the trip is updated or removed accordingly.
- Given I have a saved trip, when I choose to buy tickets for it, then I am taken to ticket purchase.

**Story 5**

As a user, I want to be told if something changes for my planned trip, so that I am not caught out on the day.

- Given I have a saved trip, when planned service changes affect its route, then I see a warning on that trip.
- Given a change affects a saved trip, when it is detected, then I am notified and can view updated route options.
- Given I have opted in to a reminder, when the chosen time before departure arrives, then I receive the reminder.
- Given I have a saved trip, when I turn off notifications for it, then I no longer receive notifications for that trip.


**Nearby Stops**

**Story 1**

As a rider, I want to see destinations near a given stop, so that I know what is around it if I do not know exactly where to get off.

- Given I select a stop from a route, the map, or a saved trip, when its details open, then I see nearby destinations with their name, category, and walking distance or time from the stop, nearest first.
- Given there are no destinations near the stop, when I view its details, then I am told none were found.

**Story 2**

As a rider, I want to filter nearby destinations by category and distance, so that I can find the kind of place I am looking for.

- Given I am viewing nearby destinations, when I choose categories such as restaurants, hotels, attractions, parks, or shops, then only destinations in those categories are shown.
- Given I am viewing nearby destinations, when I set a walking time limit, then only destinations within that limit are shown.
- Given I have applied filters, when I view the list, then I can see which filters are active and clear them.

**Story 3**

As a rider, I want to enter my destination and see which stops on my route are closest to it, so that I can choose where to get off.

- Given I have a route and enter a destination, when results are displayed, then the stops on my route are ranked by walking time, each showing walking distance, time, and the line and direction serving it.
- Given the ranked stops are displayed, when I pick one, then it is applied to my planned trip.
- Given my destination is a general area or neighborhood, when results are displayed, then I am shown the stops nearest its center.

**Story 4**

As a rider, I want to see the walking route from a stop to a destination, so that I know how to get there once I get off.

- Given I am viewing a destination near a stop, when I select it, then I see it on the map with a walking path from the stop.
- Given a walking path is displayed, when I view it, then I see the distance, estimated time, and the exit or street to take when known.
- Given a walking path is displayed, when I ask for step-by-step directions, then I receive them.
- Given I have mobility needs, when I request a walking route, then I can have stairs and steep routes avoided.

**Story 5**

As a rider, I want to see basic details about a nearby destination, so that I can decide whether it is worth getting off there.

- Given I select a nearby destination, when its details open, then I see its address, category, hours with whether it is open now, and rating when available.
- Given I am viewing a destination's details, when I choose to, then I can see it on the map or get walking directions to it.
- Given details cannot be loaded, when I open a destination, then I am told and can try again, and its name and distance are still shown.


**User Accounts**

Story 1

As a new user, I want to create an account with my email, so that the app can save my information.

- Given I am a new user, when I provide an email and a password that meets the rules shown, then my account is created and I am sent a verification message.
- Given I have received the verification message, when I confirm it, then my account is verified.
- Given I enter an email already in use, an invalid email, or a weak password, when I submit, then I am told what is wrong and how to fix it.
- Given I have not received a verification message, when I request another, then a new one is sent.

**Story 2**

As a returning user, I want to sign in and recover my account if I forget my password, so that I am never locked out of my saved information.

- Given I have a verified account, when I sign in with my credentials, then I can access my saved information and remain signed in on that device until I sign out.
- Given I have forgotten my password, when I request a reset, then I am sent a way to reset it by email.
- Given I am signed in, when I sign out, then my saved information is no longer accessible on that device until I sign in again.
- Given there are repeated failed sign-in attempts, when the limit is reached, then I am temporarily prevented from signing in and told why.

**Story 3**

As a user, I want to view and edit my contact information, so that receipts and alerts reach me.

- Given I am signed in, when I edit my name, email, or phone number and save, then the changes are saved and I receive confirmation.
- Given I change my email address, when I save, then the new address must be verified before it takes effect.
- Given I choose to delete my account, when I confirm after being told what will be lost, then my account and its data, including simulated tickets, purchase records, and saved contacts, are deleted.
- Given a save fails, when I try to save changes, then I am told and can try again.

**Story 4**

As a user, I want to save a simulated payment method and see my payment records, so that I can buy tickets quickly and keep track of what I have spent.


- Given I am signed in, when I add, edit, remove, or set a default simulated payment method, then the change is saved.
- Given I am adding a payment method, when I enter anything other than a test card number, then it is rejected and I am told that only test payments are accepted.
- Given I have saved payment methods, when I view them, then they are labeled as test methods, and full card numbers are never stored or displayed.
- Given I have made simulated purchases, when I view my payment history, then I see each charge with its date, amount, and receipt.
- Given I remove a payment method used by an active pass, when I confirm, then I am prompted to choose a replacement.

**Story 5**

As a user, I want my trip history and planned trips saved to my account, so that they are available on any device I sign in on.

- Given I am signed in, when I view my account, then I see my saved upcoming trips and past trips.
- Given I sign in on a new or replacement phone, when I am signed in, then my saved data is restored.
- Given I have saved history, when I choose to view or clear it, then I can do so from my account.
- Given I am not signed in, when I try to save something, then I am prompted to sign in or create an account.


**Crowding Data**

**Story 1**

As a rider, I want to see how crowded a stop is right now, so that I can decide whether to wait there or find a different means of transportation.

- Given I am viewing a stop, when its details are displayed, then I see its current crowding level, such as low, moderate, or high.
- Given I am viewing the map or the stops along a route, when stops are displayed, then I can see each stop's crowding level without opening its details.
- Given a crowding level is shown, when I view it, then I can see when it was last updated.
- Given a crowding level is shown, when I read it, then its meaning does not depend on color alone.

**Story 2**

As a commuter, I want to see when a stop is usually busy or quiet, so that I can pick a better time to travel.

- Given I am viewing a stop, when I look at its crowding details, then I see how crowded it typically is across the day.
- Given I am viewing typical crowding, when I choose weekday or weekend, then the pattern for that type of day is shown.
- Given I am viewing typical crowding, when I compare it with the current time, then I can tell how the current crowding compares with what is usual.
- Given I am planning a trip for a future date and time, when the results are displayed, then I see the expected crowding for that date and time.

**Story 3**

As a rider, I want suggestions when my stop is crowded, so that I can find a different means of transportation.

- Given my stop has a high crowding level, when I view it or my trip, then I am offered alternatives such as a nearby stop, another line, a bus, or a bike station.
- Given alternatives are offered, when I compare them, then I see each one's travel time and crowding level.
- Given I select an alternative, when I confirm, then my trip is updated to use it.
- Given I am offered alternatives, when I choose to dismiss them, then they are no longer shown for that stop.

**Story 4**

As a rider, I want to know whether crowding information is live or estimated, so that I know how much to trust it.

- Given a crowding level is shown, when I view it, then I am told whether it is live or estimated from typical patterns.
- Given there is no crowding data for a stop, when I view it, then I am told the information is unavailable, and no guessed value is shown.
- Given the crowding information is out of date or its source is unavailable, when I view it, then I am warned and can try again.
- Given I am viewing crowding information, when I want to know how it is measured, then I can find an explanation.


**Themes and Accessibility**

**Story 1**

As a user, I want to choose how the app looks, so that it is comfortable to use in different lighting and suits my taste.

- Given I open the appearance settings, when I view the options, then I can choose from several appearance themes, including one that follows my device's setting and a high-contrast option.
- Given I select a theme, when I confirm, then it is applied across all screens, including the map, without my having to restart the app.
- Given I have chosen a theme, when I reopen the app, then my chosen theme is still in use.
- Given I choose the high-contrast option, when I view any screen, then text and map elements meet accessibility contrast requirements.

**Story 2**

As a rider with low vision or other visual needs, I want to adjust text size and display options, so that I can read information easily.

- Given my device has a text size setting, when I open the app, then the app follows it, and I can also increase text size further within the app.
- Given I have chosen a larger text size, when I view any screen, then all text remains readable and is not cut off or overlapping.
- Given I have color vision differences, when I choose a color-blind-friendly option, then route and status colors change to suit it, and meaning is still not conveyed by color alone.
- Given I prefer less motion, when I turn on reduced motion or my device has it on, then animations and transitions are minimized.

**Story 3**

As a rider who is visually impaired or has limited dexterity, I want the app to work with assistive technology, so that I can get the same information and complete the same tasks as any other rider.

- Given I use a screen reader, when I move through any screen, then every control, marker, and image is described meaningfully and read in a logical order.
- Given I cannot use or see the visual map, when I open the map, then I can get the same route, stop, and step information as a text-based alternative.
- Given I use alternative input such as switch control, voice control, or an external keyboard, when I use the app, then I can reach and operate all features.
- Given a status changes or an error occurs, when I am using a screen reader, then the change is announced to me.

**Story 4**

As a rider with mobility needs, I want to set step-free travel preferences, so that trips and directions work for me by default.

- Given I turn on step-free travel or avoiding stairs and steep walks, when I plan a trip or request walking directions, then the results respect those preferences.
- Given I am viewing a station or stop, when its details are displayed, then I can see its accessibility information, such as whether it has an elevator.
- Given an elevator or escalator is out of service, when I view the station or a planned route that depends on it, then I am warned.
- Given I have chosen stations I use, when an elevator or escalator outage affects them, then I can be notified.

**Story 5**

As a user, I want my appearance and accessibility settings saved, so that I do not have to set them up again.

- Given I am using the app for the first time, when I begin, then I am offered the chance to set accessibility options up front.
- Given I change any setting, when I confirm, then I see it take effect and it is kept for future use.
- Given I am not signed in, when I change settings, then they are saved on my device, and once I sign in they are saved to my account.
- Given I want to undo my changes, when I choose to reset to defaults and confirm, then all settings return to their original values.


**Online Ticketing Purchasing**

**Story 1**

As a rider, I want to browse the available fares and choose the right ticket, so that I can buy what fits my trip.

- Given I open ticket purchasing, when I view the options, then I see the available ticket types, such as single ride, day pass, weekly pass, and monthly pass, each with its price and validity period.
- Given I have chosen a ticket type, when I set a quantity, then the total updates to match.
- Given I come from a planned trip, when I open ticket purchasing, then the ticket that fits that trip is suggested.
- Given reduced fares apply to some riders, when I view the ticket options, then I can see which reduced fares are available.
- Given I am viewing tickets, when I browse or buy, then I am clearly told that purchases are simulated and no real money is charged.

**Story 2**

As a rider, I want to complete a purchase with a simulated payment, so that I can get a ticket without waiting in line or using a separate service.

- Given I have chosen a ticket, when I proceed to pay, then I see a summary of my order with the ticket, quantity, and total before I confirm.
- Given I am ready to pay, when I choose a saved simulated payment method or add a new one, then it is used for the purchase.
- Given I enter payment details, when I submit anything other than a test card number, then it is rejected and I am told that only test payments are accepted.
- Given my simulated payment succeeds, when the purchase is complete, then I see a confirmation and am sent a receipt marked as a simulated purchase.
- Given my simulated payment fails, when I am told the reason, then I can try again without re-entering my order, and I am never charged twice for the same purchase.

**Story 3**

As a rider, I want to have my ticket on my phone, so that I can show it when I ride and never need paper.

- Given I have purchased a ticket, when I open it, then I see a scannable-style code, its type, and its validity or expiration.
- Given I have no signal, when I open a purchased ticket, then it still opens.
- Given I am demonstrating the app, when I use the demo validation option, then the ticket is marked as active or used, so the full ticket lifecycle can be shown.
- Given I view a ticket, when I check its status, then I can tell whether it is ready to use, active, or expired.
- Given I use a screen reader or bright light, when I view a ticket, then its details remain readable and accessible.

**Story 4**

As a rider, I want to see my tickets and purchase history, so that I can find a ticket, get a receipt, or resolve a problem.

- Given I have tickets, when I open my tickets, then active tickets are separated from used and expired ones.
- Given I have made purchases, when I view my purchase history, then I see each purchase's date, simulated amount, and receipt, consistent with my account's payment history.
- Given a ticket is eligible for a refund, when I request one, then I can see the status of my request.
- Given I sign in on a new phone, when I am signed in, then my purchased tickets are restored.


**Trip History**

**Story 1**

As a user, I want to see a log of my previous trips, so that I can look back at where I have been.

- Given I have taken trips, when I open my trip history, then I see them listed by date, newest first.
- Given I am viewing my trip history, when I look at a trip, then I see its date, origin, destination, lines and modes used, duration, and fare.
- Given I select a past trip, when its details open, then I see its full details and can view its route on the map.
- Given I have no trips recorded, when I open my trip history, then I am told how trips are recorded.

**Story 2**

As a commuter, I want to see patterns in my trips, so that I can plan for the future.

- Given I have a trip history, when I open my travel summary, then I see my most frequent routes, most-used lines, and usual travel days and times.
- Given I am viewing my summary, when I look at monthly totals, then I see my trip count and total fare spending, labeled as simulated amounts.
- Given I am viewing my summary, when I choose a time range such as the past week, month, or year, then the summary reflects that range.
- Given I use a screen reader or cannot view charts, when I open my summary, then I can get the same information in a text-based alternative.

**Story 3**

As a commuter, I want to reuse a previous trip, so that I do not have to re-enter my regular routes.

- Given I am viewing a past trip, when I choose to repeat it, then the trip planner opens with the origin and destination already filled in.
- Given I am repeating a trip, when I choose a new date and time, then the results are based on current live or scheduled information, not the original trip's.
- Given I take a route often, when I mark it as a favorite, then I can reach it quickly later.
- Given my history shows a clear pattern, when I open the app, then I am offered my frequent route as a suggestion.

**Story 4**

As a user, I want to search and control my trip history, so that I can find a trip and decide what is kept.

- Given I am viewing my trip history, when I search or filter by date range, place, line, or mode, then only matching trips are shown.
- Given I am viewing my trip history, when I delete a single trip or clear all history and confirm, then it is permanently removed from my account and my device.
- Given I am signed in, when I view my history on another device, then I see the same trips.
- Given I am not signed in, when I open my trip history, then I am told that history requires an account.


**Nearby Rental Bike Locations**

**Story 1**

As a user, I want to see rental bike stations near me, so that I know where I can pick up a bike.

- Given I open the bike stations view, when stations are displayed, then I see them on the map and in a list, nearest first, each with its name, walking distance, and number of bikes available.
- Given I am viewing stations, when I choose to show only those with bikes available, with docks available, or with e-bikes, then only matching stations are shown.
- Given I have not shared my location, when I search an address or place, then I see the stations near it.
- Given there are no stations nearby, when I view the results, then I am told none were found.

**Story 2**

As a cyclist, I want to see how many bikes and open docks a station has, so that I do not travel to an empty or full station.

- Given I select a station, when its details open, then I see the number of bikes available, e-bikes available where provided, and open docks.
- Given a station is offline or out of service, when I view it, then it is clearly labeled as unavailable and is not shown as having bikes or docks.
- Given a station has few bikes or docks left, when I view it, then I am told availability is low, and the meaning does not depend on color alone.
- Given I am viewing a station, when I look at its availability, then I can see when it was last updated, and it stays current while I have the screen open.
- Given the bike information is out of date or its source is unavailable, when I view it, then I am warned and can try again.

**Story 3**

As a user, I want directions to a bike station, so that I can reach it and start my ride.

- Given I select a station, when I ask for directions, then I see a walking route from my location with its distance and estimated time.
- Given a walking route is displayed, when I ask for step-by-step directions, then I receive them.
- Given I have set mobility needs in my preferences, when I request directions, then they respect those needs.
- Given I am viewing a station, when I want to unlock a bike, then I am directed to the bike-share provider's own app or site.

**Story 4**

As a cyclist, I want to plan trips that combine biking and transit, so that I can pick up a bike, ride, and return it smoothly.

- Given I am planning a trip, when I choose whether to include a bike leg, then the results include or exclude biking accordingly.
- Given a route includes a bike leg, when I view it, then I see the pickup station, the drop-off station, and the availability at each.
- Given the drop-off station is full or nearly full, when I view my route, then I am warned and offered a nearby station with open docks.
- Given a route includes a bike leg, when I view it on the map, then the bike leg is distinguishable from the other legs.
- Given my stop is crowded, when I view alternatives, then a nearby bike station is offered along with its availability.


**Weather Info**

**Story 1**

As a user, I want to see the current weather for my area, so that I know what to expect before I head out.

- Given I open the weather information, when it is displayed, then I see the current temperature, conditions, what it feels like, precipitation, and wind.
- Given I have shared my location, when I view the weather, then it is for my current area.
- Given I have not shared my location, when I search for a place, then I see the weather for that place.
- Given I view the weather, when I read the conditions, then they are described in words and do not depend on an image alone.
- Given I want to see temperatures in a different unit, when I change the setting, then temperatures are shown in Fahrenheit or Celsius as I chose.

**Story 2**

As a user, I want to see the forecast for the time and place I am traveling, so that I can decide how and when to go.

- Given I am viewing the weather, when I look at the forecast, then I see an hourly forecast for the next 48 hours and a daily forecast for as many days ahead as the weather source provides.
- Given I am planning a trip, when the route options are displayed, then I see the forecast for my chosen date, time, and destination.
- Given my trip date is beyond the range of the forecast, when I view the results, then I am told the forecast is not available yet, and no guessed forecast is shown.
- Given I am viewing a forecast, when I choose between my current location and my destination, then the forecast shown matches my choice.

**Story 3**

As a user, I want to be warned about severe weather and told how it affects my trip, so that I can prepare or change my plans.

- Given there is an active weather alert such as a storm, extreme heat or cold, flooding, or snow, when I view the weather or an affected trip, then I see the alert.
- Given the weather may affect my trip, when I view the weather or my route, then I see simple advice, such as bringing an umbrella or considering a covered route.
- Given my route includes walking or biking, when conditions make those legs less comfortable or safe, then I am shown a note on those legs.
- Given I have saved trips, when I choose to receive severe weather notifications, then I am notified about severe weather affecting them.

**Story 4**

As a user, I want to know how recent the weather information is, so that I can trust it.

- Given I am viewing the weather, when it is displayed, then I can see when it was last updated.
- Given the weather cannot be loaded, when I open it, then I am shown a message and can try again, and the rest of the app continues to work.
- Given my device is offline, when I view previously loaded weather, then I see the last known weather and am told it is out of date.
- Given I use a screen reader, large text, or a chosen theme, when I view the weather, then it is readable and follows those settings.


**Local Hotels and Miscellaneous Businesses**

**Story 1**

As a visiting user, I want to see hotels and other lodging near where I am or where I am headed, so that I can choose a place to stay that is easy to reach by transit.

- Given I open the lodging view, when results are displayed, then I see lodging on the map and in a list, nearest first, each with its name, type, rating, and price range where available.
- Given a lodging result is shown, when I view it, then I see the nearest stop or station and the walking time to it.
- Given I am viewing lodging, when I choose a lodging type, price range, or rating, then only matching results are shown.
- Given I have not shared my location, when I search an address, neighborhood, or landmark, then I see the lodging around it.
- Given there is no lodging in the area, when I view the results, then I am told none were found.

**Story 2**

As a visiting user, I want to browse restaurants, shops, attractions, and other businesses nearby, so that I know what is around during my stay.

- Given I open the businesses view, when I choose a category such as restaurants, cafes, attractions, shopping, groceries, pharmacies, or ATMs, then I see matching businesses on the map and in a list.
- Given I am viewing businesses, when I filter by category, distance, rating, or whether they are open now, then only matching results are shown.
- Given a business is shown, when I view it, then I see its name, category, rating, and the walking or transit time from my location.
- Given no businesses match my search, when I view the results, then I am told and prompted to widen the search area or change filters.

**Story 3**

As a visiting user, I want to see details about a hotel or business, so that I can decide whether it fits my plans.

- Given I select a hotel or business, when its details open, then I see its address, hours with whether it is open now, rating, price level, phone number, and website where available.
- Given I am viewing a place's details, when I choose to call it, visit its website, or see it on the map, then I am taken there.
- Given I am viewing a place's details, when I ask for directions, then a transit trip to the place is planned.
- Given I am viewing a place's details, when I look at how to reach it, then I see the nearest stops and lines serving it.
- Given details cannot be loaded, when I open a place, then I am told and can try again, and its name and distance are still shown.

**Story 4**

As a visiting user, I want to save places to a list, so that I can build a plan for my visit and find them again.

- Given I am viewing a hotel or business, when I save it to my list or remove it, then my list is updated.
- Given I have saved places, when I view my list, then I can see them on the map with the nearest stops and lines for each.
- Given I have a saved place, when I choose it as a destination, then it is used in the trip planner.
- Given I am signed in, when I save places, then they are kept in my account, and if I am not signed in, I am prompted to sign in or create an account.
- Given I have no connection, when I open my saved places, then I see the last known details and am told they may be out of date.


**Emergency Contact Info**

**Story 1**

As a user, I want to reach emergency and help numbers quickly, so that I can get help fast when something goes wrong.

- Given I am on any main screen, when I need help, then I can reach the emergency and help contacts without searching through menus.
- Given I open the help contacts, when the list is displayed, then I see 911, 311, transit police or the transit agency's help line, and a station or customer assistance number, and I can call any of them directly.
- Given I cannot make a voice call, when I view the help contacts, then I see text-based options, such as texting 911 where available.
- Given I am viewing a help contact, when I read it, then I see a short explanation of when to use it, such as a life-threatening emergency or a service problem.
- Given I use a screen reader or large text, when I open the emergency screen, then all contacts remain readable and usable.

**Story 2**

As a user, I want to store my own emergency contacts, so that the people I trust can be reached quickly if something happens to me.

- Given I open my emergency contacts, when I add, edit, or delete a contact with a name, phone number, and relationship, then my list is updated.
- Given I have several contacts, when I mark one as primary, then it appears first.
- Given I am not signed in, when I save contacts, then they are stored on my device, and once I sign in they are saved to my account.
- Given I select a contact, when I choose to call or text, then I am connected to that contact.
- Given I choose to delete a contact, when I am asked to confirm, then the contact is removed only after I confirm.
- Given I have no contacts saved, when I open my emergency contacts, then I am told how to add one.

**Story 3**

As a rider, I want to be pointed to help and my contacts during a serious incident, so that I know what to do and can tell someone where I am.

- Given a major disruption or incident is reported on a line I am viewing, when I view that line, then I see the relevant help contacts and safety instructions.
- Given I choose to share my location, when I select one or more saved contacts, then a message with my current location is prepared for them through my phone's messaging options.
- Given my location is not available, when I prepare a message, then it says so and includes my last known stop or route instead.
- Given a message is prepared, when I have not confirmed it, then nothing is sent.
- Given I view the emergency screen, when I read it, then I am told the app does not replace calling emergency services.

**Story 4**

As a user, I want emergency information to be available offline and up to date, so that I can rely on it when I have no signal or the service is down.

- Given I have no signal, when I open the help contacts or my personal contacts, then they are still available.
- Given I view the help contacts, when the list is displayed, then I can see when it was last updated.
- Given an update to the help contacts fails, when I open the list, then I see the last saved list and am told it may be out of date.
- Given I am an admin, when I update the help contacts or instructions, then users receive the changes without needing a new app release.
- Given I have saved personal contacts, when the app sends usage reports or error logs, then my contact data is excluded.


**Carbon Footprint Tracker**

**Story 1**

As a user, I want to see the estimated carbon emissions of a trip, so that I can understand the environmental impact of how I travel.

- Given I am viewing route options, when the results are displayed, then each option shows its estimated CO₂ emissions.
- Given an estimate is shown, when I view it, then I can see how it compares with making the same trip by car, as an amount and a percentage saved.
- Given my route includes walking or biking, when I view the estimate, then those parts are shown as producing little or no emissions.
- Given I open a trip's details, when I view its emissions, then I see the breakdown by leg and mode of travel.
- Given an impact is shown, when I read it, then its meaning does not depend on color alone.

**Story 2**

As a user, I want to see my total carbon impact over time, so that I can see how my transit use helps the environment.

- Given I have recorded trips, when I open my carbon summary, then I see my total CO₂ emissions and the CO₂ avoided compared with driving.
- Given I am viewing my summary, when I choose a time range such as the past week, month, or year, then the totals and trend reflect that range.
- Given I am viewing my totals, when I look at what they mean, then they are also shown in relatable terms, such as miles not driven or gallons of gas avoided.
- Given I use a screen reader or cannot view charts, when I open my summary, then I can get the same information as text.
- Given I have no recorded trips, when I open my carbon summary, then I am told how the tracker gets its data.

**Story 3**

As a user, I want to know how my carbon numbers are calculated, so that I can trust them.

- Given I am viewing any carbon figure, when I want to know how it was calculated, then I can find an explanation of the distance, mode, and emission factors used.
- Given a figure is shown, when I view it, then it is labeled as an estimate, and the source and year of the emission factors are available.
- Given I drive a different type of vehicle than the average, when I choose my comparison vehicle, then the "avoided" figures reflect my choice.
- Given the emissions data cannot be loaded, when I view a carbon figure, then I see the last saved values and am told they may be out of date, or I am told an estimate is not available.

**Story 4**

As a user, I want to set a goal and see my progress, so that I stay motivated to keep using public transportation.

- Given I open the carbon tracker, when I set a goal such as CO₂ avoided this month or number of car-free trips, then the goal is saved.
- Given I have a goal, when I view my progress, then I can see how close I am, and I am congratulated when I reach it.
- Given I want to share my progress, when I choose to share, then a summary is sent through my phone's sharing options, and it does not include my locations or trip details.
- Given I do not want goals or progress messages, when I turn them off, then they are no longer shown, and I receive no notifications about them.


**Onboarding Resources**

**Story 1**

As a joining user, I want a short walkthrough the first time I open the app, so that I understand what it does and where to find things.

- Given I am opening the app for the first time, when I begin, then I am shown a short introduction to the main areas: the map, trip planner, live updates, tickets, bike stations, weather, and emergency help.
- Given I am viewing the walkthrough, when I choose to skip it, then I can leave it at any point, and I can see how much of it remains while I am in it.
- Given the app needs my location or notifications, when the walkthrough reaches that point, then I am told why before I am asked for permission, and the app works fully if I decline.
- Given I do not have an account, when I finish the walkthrough, then I am offered the chance to create one, and I can use the app without doing so.
- Given I use a screen reader, large text, or reduced motion, when I view the walkthrough, then it works with those settings, and I am offered accessibility options up front.

**Story 2**

As a user, I want a help section I can open at any time, so that I can find out how to do something without leaving the app.

- Given I am using the app, when I open help, then I see topics organized by feature.
- Given I am in the help section, when I search for a topic or question, then I see matching results, and if none match, I am shown suggestions.
- Given I have already completed the walkthrough, when I choose to replay it from help, then the full walkthrough is shown again.
- Given I open a feature for the first time, when it is displayed, then I am shown a brief tip that I can dismiss, and I can turn tips off in settings.
- Given I need more help, when I contact support or report a problem from the help section, then my request is submitted and I can see its status.

**Story 3**

As a joining user, I want guidance that matches how I will use the app, so that I learn what matters to me first.

- Given I am in the walkthrough or help section, when I choose how I will use the app, such as commuting, visiting, accessibility needs, or cycling, then I can select more than one or none.
- Given I have chosen one or more paths, when I view the guidance, then it highlights the features relevant to me, such as saved routes and alerts for commuters, nearby places for visitors, step-free routing for accessibility needs, and bike stations for cyclists.
- Given I want to practice, when I choose the guided practice, then I am walked through planning a sample trip using clearly labeled sample data, and nothing in my account changes.
- Given I am learning how to buy tickets, when I view that guidance, then I am told that purchases are simulated.
- Given I have chosen a path, when I choose to change or reset it, then my selection is updated.

**Story 4**

As an admin, I want to update tutorial and help content and see how it is being used, so that the guide stays accurate and improves over time.

- Given I am an admin, when I add, edit, or remove tutorial or help content, then users receive the changes without needing a new app release.
- Given I have no signal, when I open the guide, then it still opens, and I can see when it was last updated.
- Given an update to the content fails to load, when I open the guide, then I see the last saved content.
- Given I am viewing a help topic, when I mark it as helpful or not, then my feedback is recorded.
- Given I am an admin, when I view usage reports, then I see anonymous information such as which topics are viewed and where users skip the walkthrough.
- Given reports and error logs are sent to the team, when they are received, then they contain no personal information.
