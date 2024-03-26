import React, { useState, useEffect } from 'react';
import { Collapse, Card, ListGroup } from 'react-bootstrap';
import './Category_sidebar.css';

const CategoryTree = ({ categories, parent_id = null, setSelectedCategory, level = 0 }) => {
    const [open, setOpen] = useState({});

    const handleClick = (id) => {
        setOpen(prevOpen => ({ ...prevOpen, [id]: !prevOpen[id] }));
        setSelectedCategory(id);
    };

    const subcategories = categories.filter(cat => cat.parent_id === parent_id);

    return (
        <>
            {subcategories.map(category => (
                <div key={category.id} style={{ paddingLeft: `${level * 20}px` }}>
                    <ListGroup.Item
                        onClick={() => handleClick(category.id)}
                        action
                        className="text-left"
                    >
                        {category.name}
                    </ListGroup.Item>
                    <Collapse in={open[category.id] || false}>
                        <div id={`category-collapse-${category.id}`}>
                            <CategoryTree categories={categories} parent_id={category.id} setSelectedCategory={setSelectedCategory} level={level + 1} />
                        </div>
                    </Collapse>
                </div>
            ))}
        </>
    );
};

const CategorySidebar = ({ categories, setSelectedCategory }) => {
    return (
        <Card className="sidebar">
            <Card.Header>Categories</Card.Header>
            <ListGroup variant="flush">
                <ListGroup.Item
                    onClick={() => setSelectedCategory(null)}
                    action
                    className="text-left"
                >
                    All
                </ListGroup.Item>
                <CategoryTree categories={categories} setSelectedCategory={setSelectedCategory} />
            </ListGroup>
        </Card>
    );
};

export default CategorySidebar;