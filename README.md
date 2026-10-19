# SWE Capstone Project

**Team Members:** Caceres, Jainny; Mushorn, Zachary; Quigley, Paul; Samaniego, Jorge; Yalcinkaya, Kevin


## Proposal #1 - Work Order Ticketing System

**Description:** A web-based application which allows for the submission of tickets for work orders. The app would feature handling for user IDs, user roles/groups, ticket status tracking, display analytics, and ensuring the assignment of individual tickets to the appropriate users or groups. This project would require a frontend toolkit for the GUI alongside a database API such as Mongo for storage of relevant data.


## Proposal #2 - Self-Hosted Video Sharing App

**Description:** A web-based video sharing application which features comments on individual videos, ratings, content recommendations, multi-authored videos, and internal web traffic statistics. As an open-source application, the novelty of this app exists in its ability to be self-hosted and self-governed. We anticipate that we'll be using an open-source tool such as HandBrake to handle video encoding, an API to facilitate user authentication, an API for the frontend GUI, and Mongo for the necessary databases. 


## Proposal #3 - Public Transit App

**Description:** A mobile application that helps users search for public transportation and travel without any issues. This application would be perfect for daily public transportation commuters, student who commute, tourists and many more. Transportation can be very overwhelming due to many aspects when it comes to traveling. This app would help users find the best option for their trips with an interactive map route, real-time transit updates, a trip planner, nearby-stops in the area, and crowding information. For this project, frontend like React can possibly work and a database such as Mongo would be convenient. 


# Prototype

[TransitHub NYC Figma prototype](https://www.figma.com/proto/nCVNZNOuAAg0WNidMlfrSv/UI-Prototype-TransitHub-NY?node-id=3-217&p=f&t=NNRyeE9Sxl2l4PPX-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1&starting-point-node-id=3%3A217)

## UX

<img width="855" height="607" alt="Screen_Shot_2026-10-18_at_5 17 35_PM" src="https://github.com/user-attachments/assets/9781d698-46e4-4ed1-a21c-09d252cab240" />

## Context Diagram

<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="660" viewBox="0 0 1100 660">
<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">
<path d="M0 1 L9 5 L0 9 z" fill="#A7ADB5"/></marker></defs>
<rect width="1100" height="660" fill="#F7F8FA"/>
<rect x="450" y="250" width="200" height="110" rx="12" fill="#CFE3F7" stroke="#C5DBF1" stroke-width="1.5"/><text x="550.0" y="299.0" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="19" font-weight="bold" fill="#2A5DA8">TransitHub NYC</text><text x="550.0" y="321.0" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#2A5DA8">Django backend + MongoDB</text><rect x="40" y="270" width="160" height="70" rx="12" fill="#DCEBF9" stroke="#C5DBF1" stroke-width="1.5"/><text x="120.0" y="310.0" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#2A5DA8">Rider</text><rect x="900" y="270" width="160" height="70" rx="12" fill="#DCEBF9" stroke="#C5DBF1" stroke-width="1.5"/><text x="980.0" y="310.0" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#2A5DA8">Admin</text><rect x="420" y="40" width="260" height="70" rx="12" fill="#DCEBF9" stroke="#C5DBF1" stroke-width="1.5"/><text x="550.0" y="69.0" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#2A5DA8">MTA Data Feeds</text><text x="550.0" y="91.0" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#2A5DA8">GTFS + GTFS-Realtime</text><rect x="420" y="530" width="260" height="70" rx="12" fill="#DCEBF9" stroke="#2A5DA8" stroke-width="1.5" stroke-dasharray="7 5"/><text x="550.0" y="559.0" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="15" font-weight="bold" fill="#2A5DA8">Map Service</text><text x="550.0" y="581.0" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="13" fill="#2A5DA8">Map tiles, geocoding</text><line x1="200" y1="290" x2="446" y2="290" stroke="#A7ADB5" stroke-width="1.6" marker-end="url(#ah)"/><rect x="225.0" y="236.0" width="196" height="38" rx="11" fill="#EAF2FC" stroke="#C5DBF1" stroke-width="1"/><text x="323" y="251.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">Trip searches, location,</text><text x="323" y="267.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">login, ticket requests</text><line x1="450" y1="330" x2="204" y2="330" stroke="#A7ADB5" stroke-width="1.6" marker-end="url(#ah)"/><rect x="220.0" y="347.0" width="206" height="38" rx="11" fill="#EAF2FC" stroke="#C5DBF1" stroke-width="1"/><text x="323" y="362.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">Routes, live delays, alerts,</text><text x="323" y="378.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">crowding, trip history</text><line x1="900" y1="290" x2="654" y2="290" stroke="#A7ADB5" stroke-width="1.6" marker-end="url(#ah)"/><rect x="702.0" y="236.0" width="150" height="38" rx="11" fill="#EAF2FC" stroke="#C5DBF1" stroke-width="1"/><text x="777" y="251.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">Alert and route</text><text x="777" y="267.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">updates</text><line x1="650" y1="330" x2="896" y2="330" stroke="#A7ADB5" stroke-width="1.6" marker-end="url(#ah)"/><rect x="712.0" y="351.0" width="130" height="22" rx="11" fill="#EAF2FC" stroke="#C5DBF1" stroke-width="1"/><text x="777" y="366.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">Usage reports</text><line x1="520" y1="110" x2="520" y2="246" stroke="#A7ADB5" stroke-width="1.6" marker-end="url(#ah)"/><rect x="340.0" y="161.0" width="160" height="38" rx="11" fill="#EAF2FC" stroke="#C5DBF1" stroke-width="1"/><text x="420" y="176.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">Schedules, real-time</text><text x="420" y="192.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">arrivals, alerts</text><line x1="580" y1="250" x2="580" y2="114" stroke="#A7ADB5" stroke-width="1.6" marker-end="url(#ah)"/><rect x="600.0" y="169.0" width="120" height="22" rx="11" fill="#EAF2FC" stroke="#C5DBF1" stroke-width="1"/><text x="660" y="184.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">Feed requests</text><line x1="520" y1="360" x2="520" y2="526" stroke="#A7ADB5" stroke-width="1.6" marker-end="url(#ah)"/><rect x="355.0" y="426.0" width="140" height="38" rx="11" fill="#EAF2FC" stroke="#C5DBF1" stroke-width="1"/><text x="425" y="441.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">Map and address</text><text x="425" y="457.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">lookups</text><line x1="580" y1="530" x2="580" y2="364" stroke="#A7ADB5" stroke-width="1.6" marker-end="url(#ah)"/><rect x="610.0" y="426.0" width="110" height="38" rx="11" fill="#EAF2FC" stroke="#C5DBF1" stroke-width="1"/><text x="665" y="441.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">Map tiles,</text><text x="665" y="457.5" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="12.5" font-weight="bold" fill="#2A5DA8">coordinates</text><rect x="40" y="612" width="34" height="18" rx="5" fill="#DCEBF9" stroke="#2A5DA8" stroke-width="1.2" stroke-dasharray="5 4"/><text x="84" y="626" font-family="Helvetica, Arial, sans-serif" font-size="12.5" fill="#2A5DA8">Dashed = assumed external service (not yet confirmed)</text>
</svg>

## Architecture

```mermaid
flowchart TB
    subgraph APP["Mobile app"]
        RIDER["Rider screens<br/>Map, trips, alerts, tickets"]
        ADMIN["Admin screens<br/>Reports, alerts, routes"]
    end

    subgraph BACKEND["Django backend (layered monolith)"]
        API["API layer<br/>Django views, URL routing"]
        SERVICE["Service layer<br/>Business rules, per module"]
        DATA["Data layer<br/>Models, storage, feed access"]
        API --> SERVICE --> DATA
    end

    DB[("MongoDB<br/>Users, trips, reports")]
    MTA["MTA feeds<br/>GTFS + GTFS-Realtime"]

    RIDER -->|"HTTPS / REST (client-server)"| API
    ADMIN -->|"HTTPS / REST"| API
    DATA --> DB
    DATA --> MTA

    classDef client fill:#cbeaf3,stroke:#2c4262,color:#2c4262
    classDef layer fill:#2c4262,stroke:#031f38,color:#ffffff
    classDef external fill:#ffffff,stroke:#2c4262,color:#2c4262
    class RIDER,ADMIN client
    class API,SERVICE,DATA layer
    class DB,MTA external

    style APP fill:#f3fafc,stroke:#2c4262,color:#2c4262
    style BACKEND fill:#e4f2f7,stroke:#2c4262,color:#2c4262
```

TransitHub NYC uses a client-server architecture. A mobile app, with screens for riders and for admins, sends requests over HTTPS and REST to a single Django backend. The backend is a monolith organized into three layers: an API layer that handles requests, a service layer that holds the business rules, and a data layer that reads and writes MongoDB and pulls routes, stops, and live alerts from the MTA's feeds.

## Test Plan

*Unit test: trip history filter check.* This test makes sure the Trip History screen shows the right trips when a rider taps a filter (All, Subway, Bus, or Rail), meaning a filter returns only trips of that transport type, newest first. We will make up four past trips for a fake rider: two subway trips, one bus trip, and one rail trip, each with a different date and time. We will then run the filtering function once with the Bus filter and check that exactly one trip comes back, the bus trip. We will also check that the All filter returns all four trips with the newest first, and that a filter with no matching trips returns an empty list instead of an error. The expected results come from the rule, not from whatever the code currently returns, so the test can catch a mistake such as a filter that lets subway trips through.

*Integration test: trip history privacy check.* This test makes sure the parts of the backend work together to keep each rider's trip history private. We will create two fake riders, Rider A with two trips and Rider B with one, and save them in a test database. We will then log in as Rider A, request the trip history through the real API, and check that exactly Rider A's two trips come back and none of Rider B's. We will also send the same request without logging in and check that it is rejected. This runs the API layer, service layer, and data layer together against a test database, so it can catch problems that only show up when the pieces are connected, such as a query that forgets to filter by rider.
