import { useEffect, useState } from "react";
import type { ChangeEvent, CSSProperties } from "react";
import Sidebar from "../components/Sidebar";

type TeamMember = {
  name: string;
  role: string;
  post: string;
  photo?: string;
};

const teamMembers: TeamMember[] = [
  {
    name: "Viraj Chaudhari",
    role: "Project Leader & Frontend Engineer",
    post: "Leads the Team and Responsible for the Frontend Development and UI design of the Project While Coordinating with the Team Members to Ensure the Project",
  },
  {
    name: "Sneh Paghadal",
    role: "Main Backend Developer",
    post: "Builds the detection pipeline that identifies people, vehicles, movement, and safety conditions.",
  },
  {
    name: "Mahi Ramani",
    role: "Presentation & Pitching",
    post: "Connects the AI pipeline to reliable Flask APIs that return clear and explainable risk results.",
  },
  {
    name: "Hetvi Patel",
    role: "Supportive Backend Devloper",
    post: "Turns complex detection output into a calm interface that teams can understand at a glance.",
  },
  {
    name: "Nisarg Bhandari",
    role: "Database Devloper & Website Analyzer",
    post: "Shapes the risk model so every percentage is traceable to a visible safety factor.",
  },
  {
    name: "Dhrumil Dhandhukiya",
    role: "Documentation & Team Memeber",
    post: "Makes the product easier to learn, present, and use responsibly in real workplace scenarios.",
  },
];

export default function TeamPage() {
  const [members, setMembers] = useState<TeamMember[]>(teamMembers);
  const [photoFrameHeight, setPhotoFrameHeight] = useState(128);
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    const savedMembers = window.localStorage.getItem("Safesight-Team-Members");
    const savedFrameHeight = Number(window.localStorage.getItem("Safesight-Team-Photo-Frame-Height"));
    if (Number.isFinite(savedFrameHeight) && savedFrameHeight >= 96 && savedFrameHeight <= 240) {
      setPhotoFrameHeight(savedFrameHeight);
    }
    if (savedMembers) {
      try {
        setMembers(JSON.parse(savedMembers) as TeamMember[]);
      } catch {
        window.localStorage.removeItem("Safesight-Team-Members");
      }
    }
  }, []);

  const updateMember = (index: number, field: keyof TeamMember, value: string) => {
    setMembers((currentMembers) => currentMembers.map((member, memberIndex) => memberIndex === index ? { ...member, [field]: value } : member));
  };

  const updateMemberPhoto = (index: number, event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => updateMember(index, "photo", typeof reader.result === "string" ? reader.result : "");
    reader.readAsDataURL(file);
  };

  const saveMembers = () => {
    window.localStorage.setItem("Safesight-Team-Members", JSON.stringify(members));
    window.localStorage.setItem("Safesight-Team-Photo-Frame-Height", String(photoFrameHeight));
    setIsEditing(false);
  };

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="dashboard-card team-page">
        <header className="page-heading team-heading">
          <div>
            <span className="eyebrow">The people behind SafeSight</span>
            <h1>About the team</h1>
            <p>Six disciplines working together to make serious injury and fatality risk easier to see and act on.</p>
          </div>
          <button className="team-edit-button" type="button" onClick={isEditing ? saveMembers : () => setIsEditing(true)}>{isEditing ? "Save team" : "Edit team"}</button>
        </header>

        <section className="team-intro">
          <span className="kicker">Built for safer decisions</span>
          <h2>From detection to direction.</h2>
          <p>SafeSight brings computer vision, explainable risk scoring, and practical interface design into one inspection workflow for workplace safety teams.</p>
          {isEditing && <label className="frame-size-control"><span>Photo frame size <strong>{photoFrameHeight}px</strong></span><input type="range" min="96" max="240" step="4" value={photoFrameHeight} onChange={(event) => setPhotoFrameHeight(Number(event.target.value))} /></label>}
        </section>

        <section className="team-grid" aria-label="SafeSight team members" style={{ "--team-photo-height": `${photoFrameHeight}px` } as CSSProperties}>
          {members.map((member, index) => (
            <article className="team-card" key={`${member.name}-${index}`}>
              <div className={`team-photo-area ${member.photo ? "has-photo" : ""}`}>
                {member.photo ? <img className="team-photo-preview" src={member.photo} alt={`${member.name} profile`} /> : <span className="team-photo-placeholder">Add photo</span>}
                <span className="team-number-only">0{index + 1}</span>
              </div>
              <div className="team-card-body">
                {isEditing && <div className="team-photo-controls"><label className="photo-upload"><span>{member.photo ? "Replace photo" : "Add photo"}</span><input type="file" accept="image/*" onChange={(event) => updateMemberPhoto(index, event)} /></label>{member.photo && <button className="photo-remove" type="button" onClick={() => updateMember(index, "photo", "")}>Remove</button>}</div>}
                {isEditing ? <label className="team-field"><span>Name</span><input value={member.name} onChange={(event) => updateMember(index, "name", event.target.value)} /></label> : <h3>{member.name}</h3>}
                {isEditing ? <label className="team-field"><span>Role / post</span><input value={member.role} onChange={(event) => updateMember(index, "role", event.target.value)} /></label> : <span className="team-role">{member.role}</span>}
                {isEditing ? <label className="team-field"><span>Contribution</span><textarea value={member.post} onChange={(event) => updateMember(index, "post", event.target.value)} rows={4} /></label> : <div className="team-post"><span>Contribution</span><strong>{member.post}</strong></div>}
              </div>
            </article>
          ))}
        </section>
      </main>
    </div>
  );
}